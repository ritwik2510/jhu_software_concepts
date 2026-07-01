"""code for query_data.py""" # pylint: disable=duplicate-code
import os
import psycopg2
from psycopg2 import sql

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "gradcafe"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
    "port": os.getenv("DB_PORT", "5432"),
}


def connect():
    """connects to the database"""
    return psycopg2.connect(**DB_CONFIG)


def safe_limit(n, default=10, minimum=1, maximum=100):
    """safely limits a number to a given range"""
    try:
        n = int(n)
    except (TypeError, ValueError):
        n = default
    return max(minimum, min(n, maximum))


def run_query(cur, title, query, params=None):
    """runs a query and prints the results"""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    cur.execute(query, params or ())
    results = cur.fetchall()
    for row in results:
        print(row)


def main():
    """main function"""
    query_data()


def query_data():
    """queries the database and prints the results"""
    conn = connect()
    cur = conn.cursor()

    run_query(
        cur,
        "1. Total Fall 2026 applications",
        sql.SQL("SELECT COUNT(*) FROM applicants WHERE term = %s LIMIT %s"),
        ("Fall 2026", safe_limit(1)),
    )

    run_query(
        cur,
        "2. % International Students",
        sql.SQL("""
            SELECT ROUND(
                100.0 * SUM(
                    CASE WHEN LOWER(COALESCE(us_or_international,'')) LIKE '%international%'
                    THEN 1 ELSE 0 END
                ) / NULLIF(COUNT(*), 0),
            2)
            FROM applicants
            LIMIT %s
        """),
        (safe_limit(1),),
    )

    run_query(
        cur,
        "3. Average GPA and GRE scores",
        sql.SQL("""
            SELECT
                ROUND(AVG(gpa)::numeric, 2),
                ROUND(AVG(gre)::numeric, 2),
                ROUND(AVG(gre_v)::numeric, 2),
                ROUND(AVG(gre_aw)::numeric, 2)
            FROM applicants
            WHERE gpa IS NOT NULL
            LIMIT %s
        """),
        (safe_limit(1),),
    )

    run_query(
        cur,
        "4. GPA of American Students (Fall 2026)",
        sql.SQL("""
            SELECT ROUND(AVG(gpa)::numeric, 2)
            FROM applicants
            WHERE term = %s
            AND gpa IS NOT NULL
            AND (
                LOWER(us_or_international) LIKE '%american%'
                OR LOWER(us_or_international) LIKE '%us%'
                OR LOWER(us_or_international) LIKE '%domestic%'
                OR LOWER(us_or_international) LIKE '%usa%'
            )
            LIMIT %s
        """),
        ("Fall 2026", safe_limit(1)),
    )

    run_query(
        cur,
        "5. Percentage of Acceptances (Fall 2026)",
        sql.SQL("""
            SELECT ROUND(
                100.0 * SUM(CASE WHEN status ILIKE '%accept%' THEN 1 ELSE 0 END)
                / NULLIF(COUNT(*), 0),
            2)
            FROM applicants
            WHERE term = %s
            LIMIT %s
        """),
        ("Fall 2026", safe_limit(1)),
    )

    run_query(
        cur,
        "6. GPA of Accepted Students",
        sql.SQL("""
            SELECT ROUND(AVG(gpa)::numeric, 2)
            FROM applicants
            WHERE status ILIKE '%accept%'
            AND term = %s
            LIMIT %s
        """),
        ("Fall 2026", safe_limit(1)),
    )

    run_query(
        cur,
        "7. JHU MS Computer Science Applicants",
        sql.SQL("""
            SELECT COUNT(*)
            FROM applicants
            WHERE LOWER(llm_generated_university) LIKE '%johns hopkins%'
            AND LOWER(llm_generated_program) LIKE '%computer%'
            AND (
                llm_generated_program ILIKE '%MS%'
                OR llm_generated_program ILIKE '%M.S%'
                OR llm_generated_program ILIKE '%Masters%'
            )
            LIMIT %s
        """),
        (safe_limit(1),),
    )

    run_query(
        cur,
        "8. PhD Acceptances",
        sql.SQL("""
            SELECT COUNT(*)
            FROM applicants
            WHERE status ILIKE '%accept%'
            AND term = %s
            AND (
                llm_generated_program ILIKE '%PhD%'
                OR program ILIKE '%PhD%'
            )
            LIMIT %s
        """),
        ("Fall 2026", safe_limit(1)),
    )

    run_query(
        cur,
        "9. LLM Comparison",
        sql.SQL("""
            SELECT
                COUNT(*) FILTER (WHERE llm_generated_program IS NOT NULL),
                COUNT(*) FILTER (WHERE llm_generated_university IS NOT NULL)
            FROM applicants
            LIMIT %s
        """),
        (safe_limit(1),),
    )

    run_query(
        cur,
        "10. Average GPA by status",
        sql.SQL("""
            SELECT
                status,
                ROUND(AVG(gpa)::numeric, 2)
            FROM applicants
            WHERE gpa IS NOT NULL
            GROUP BY status
            ORDER BY AVG(gpa) DESC
            LIMIT %s
        """),
        (safe_limit(100),),
    )

    limit = safe_limit(10)

    run_query(
        cur,
        "11. Top programs",
        sql.SQL("""
            SELECT program, COUNT(*) AS total
            FROM applicants
            GROUP BY program
            ORDER BY total DESC
            LIMIT %s
        """),
        (limit,),
    )

    cur.close()
    conn.close()


if __name__ == "__main__":
    query_data()
