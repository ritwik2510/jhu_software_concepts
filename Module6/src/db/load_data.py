"""code for loading data"""
import json
import os
import psycopg2

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "dbname": os.getenv("DB_NAME", "gradcafe"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
    "port": os.getenv("DB_PORT", "5432"),
}


def main():
    """main function"""
    print("loading data into DB")
    load_data()


def connect():
    """connects to the database"""
    return psycopg2.connect(**DB_CONFIG)


def load_data():
    """loads the data into the database"""
    conn = connect()
    cur = conn.cursor()

    try:
        with open("llm_extend_applicant_data.json", "r", encoding="utf-8") as f:
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


if __name__ == "__main__":
    load_data()
