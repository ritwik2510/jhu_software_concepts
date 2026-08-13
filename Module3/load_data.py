import json
import os
import psycopg2

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "dbname": os.environ.get("DB_NAME", "gradcafe"),
    "user": os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", "postgres")
}


def connect():
    return psycopg2.connect(**DB_CONFIG)


def load_data():
    conn = connect()
    cur = conn.cursor()

    with open("llm_extend_applicant_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Total records found: {len(data)}")

    inserted = 0
    skipped = 0

    for i, row in enumerate(data):
        if not row.get("program"):
            continue

        try:
            cur.execute("""
                    INSERT INTO applicants (
                        degree,
                        university,
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
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (url) DO NOTHING
                """, (
                    row.get("degree"),
                    row.get("university"),
                    row.get("program"),
                    row.get("comments"),
                    row.get("added_on"),
                    row.get("url"),
                    row.get("status"),
                    row.get("term"),
                    row.get("international"),
                    row.get("gpa"),
                    row.get("gre"),
                    row.get("gre_v"),
                    row.get("gre_aw"),
                    row.get("llm_generated_program"),
                    row.get("llm_generated_university")
                ))

            conn.commit()

            if cur.rowcount == 0:
                skipped += 1
            else:
                inserted += 1

        except Exception as e:
            conn.rollback()
            print("Error on row", i, ":", e)
            continue

        if i > 0 and i % 500 == 0:
            print(f"Processed {i} rows...")

    cur.close()
    conn.close()

    print(f"DONE LOADING DATA INTO POSTGRES - inserted {inserted}, skipped {skipped} duplicates")


if __name__ == "__main__":
    load_data()