import json
import os

import pika
import psycopg2
from psycopg2.extras import execute_values

from etl.scrape import fetch_new_records

EXCHANGE = "tasks"
QUEUE = "tasks_q"
ROUTING_KEY = "tasks"

DATABASE_URL = os.environ["DATABASE_URL"]


def handle_scrape_new_data(conn, payload: dict) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT last_seen FROM ingestion_watermarks WHERE source = %s",
            ("scraper",),
        )
        row = cur.fetchone()
        since = payload.get("since") or (row[0] if row else None)

        new_records = fetch_new_records(since=since)

        if not new_records:
            print("No new records found.")
            return

        rows = [
            (r["id"], r.get("name"), r.get("program"), r.get("status"), r.get("submitted_at"))
            for r in new_records
        ]

        execute_values(
            cur,
            """
            INSERT INTO applicants (id, name, program, status, submitted_at)
            VALUES %s
            ON CONFLICT (id) DO NOTHING
            """,
            rows,
        )

        max_seen = max(r["submitted_at"] for r in new_records)
        cur.execute(
            """
            INSERT INTO ingestion_watermarks (source, last_seen, updated_at)
            VALUES (%s, %s, now())
            ON CONFLICT (source)
            DO UPDATE SET last_seen = EXCLUDED.last_seen, updated_at = now()
            """,
            ("scraper", str(max_seen)),
        )

        print(f"Inserted {len(new_records)} new records. Watermark advanced to {max_seen}.")


def handle_recompute_analytics(conn, payload: dict) -> None:
    with conn.cursor() as cur:
        cur.execute("REFRESH MATERIALIZED VIEW IF EXISTS applicant_summary")
    print("Analytics recomputed.")


TASK_MAP = {
    "scrape_new_data": handle_scrape_new_data,
    "recompute_analytics": handle_recompute_analytics,
}


def _on_message(ch, method, _properties, body):
    db_conn = psycopg2.connect(DATABASE_URL)
    try:
        message = json.loads(body)
        kind = message.get("kind")
        payload = message.get("payload", {})
        print(f"Received task: {kind}")

        handler = TASK_MAP.get(kind)

        if handler is None:
            print(f"Unknown task kind '{kind}'. Discarding.")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return

        try:
            handler(db_conn, payload)
            db_conn.commit()
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print(f"Task '{kind}' completed successfully.")
        except Exception as exc:
            db_conn.rollback()
            print(f"Task '{kind}' failed: {exc}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    finally:
        db_conn.close()


def main() -> None:
    url = os.environ["RABBITMQ_URL"]
    params = pika.URLParameters(url)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()

    ch.exchange_declare(exchange=EXCHANGE, exchange_type="direct", durable=True)
    ch.queue_declare(queue=QUEUE, durable=True)
    ch.queue_bind(exchange=EXCHANGE, queue=QUEUE, routing_key=ROUTING_KEY)

    ch.basic_qos(prefetch_count=1)
    ch.basic_consume(queue=QUEUE, on_message_callback=_on_message)

    print("Worker is ready. Waiting for tasks...")
    try:
        ch.start_consuming()
    except KeyboardInterrupt:
        ch.stop_consuming()
    finally:
        conn.close()


if __name__ == "__main__":
    main()