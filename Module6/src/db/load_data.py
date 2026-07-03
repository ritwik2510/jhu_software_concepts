"""code for loading data"""
import json
import os

import psycopg2

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/gradcafe",
)

DATA_PATH = os.environ.get(
    "DATA_PATH",
    "/app/data/llm_extend_applicant_data.json",
)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS applicants (
    id                      SERIAL PRIMARY KEY,
    program                 TEXT,
    comments                TEXT,
    date_added              TEXT,
    url                     TEXT,
    status                  TEXT,
    term                    TEXT,
    us_or_international     TEXT,
    gpa                     TEXT,
    gre                     TEXT,
    gre_v                   TEXT,
    gre_aw                  TEXT,
    llm_generated_program   TEXT,
    llm_generated_university TEXT
);

CREATE TABLE IF NOT EXISTS ingestion_watermarks (
    source      TEXT PRIMARY KEY,
    last_seen   TEXT,
    updated_at  TIMESTAMPTZ DEFAULT now()
);
"""


def connect():
    """connects to the database"""
    return psycopg2.connect(DATABASE_URL)


def init_schema(conn) -> None:
    """creates the database tables if they don't exist"""
    with conn.cursor() as cur:
        cur.execute(SCHEMA_SQL)
    conn.commit()
    print("Schema ready.")


def load_data():
    """loads the data into the database"""
    conn = connect()
    cur = conn.cursor()

    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        print(f"Total records found: {len(data)}")

        for i, row in enumerate(data):
            if not row.get("program"):
                continue

            try:
                cur.execute(
                    """
                    INSERT INTO applicants (
                        program,
                        comments,
                        date_added,
                        url,
                        status,
                        term,
                        us_or_international,
                        gpa,
                        gre,
                        gre_v,
                        gre_aw,
                        llm_generated_program,
                        llm_generated_university
                    )
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        row.get("program"),
                        row.get("comments"),
                        row.get("date_added"),
                        row.get("url"),
                        row.get("status"),
                        row.get("term"),
                        row.get("international"),
                        row.get("gpa"),
                        row.get("gre"),
                        row.get("gre_v"),
                        row.get("gre_aw"),
                        row.get("llm_generated_program"),
                        row.get("llm_generated_university"),
                    ),
                )

            except Exception as e:  # pylint: disable=broad-exception-caught
                conn.rollback()
                print("Error on row", i, ":", e)
                continue

            if i > 0 and i % 500 == 0:
                conn.commit()
                print(f"Inserted {i} rows...")

        conn.commit()

    except Exception as e:  # pylint: disable=broad-exception-caught
        print("Failed to load data:", e)

    finally:
        cur.close()
        conn.close()

    print("DONE LOADING DATA INTO POSTGRES")


def main():
    """main function"""
    print("loading data into DB")
    conn = connect()
    try:
        init_schema(conn)
    finally:
        conn.close()
    load_data()


if __name__ == "__main__":
    main()