import json
import os
import psycopg2


def get_db_url():
    return os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost/gradcafe")


def connect(db_url=None):
    return psycopg2.connect(db_url or get_db_url())


def load_data(db_url=None, filename="llm_extend_applicant_data.json", data=None):
    conn = connect(db_url)
    cur = conn.cursor()

    inserted = 0
    skipped = 0

    try:
        if data is None:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)

        print(f"Total records found: {len(data)}")

        for i, row in enumerate(data):
            if not row.get("program"):
                continue

            try:
                cur.execute("""
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
                    ON CONFLICT (url) DO NOTHING
                """, (
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
                    row.get("llm_generated_university")
                ))

                conn.commit()

                if cur.rowcount == 0:
                    skipped += 1
                else:
                    inserted += 1

            except psycopg2.Error as e:
                conn.rollback()
                print("Error on row", i, ":", e)
                continue

        print(f"Inserted {inserted}, skipped {skipped} duplicates")

    except (OSError, json.JSONDecodeError, psycopg2.Error) as e:
        print("Failed to load data:", e)

    finally:
        cur.close()
        conn.close()

    print("DONE LOADING DATA INTO POSTGRES")
    return {"inserted": inserted, "skipped": skipped}


def main(db_url=None):
    load_data(db_url)


if __name__ == "__main__":
    main()