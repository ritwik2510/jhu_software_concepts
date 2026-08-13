"""Database query functions for the GradCafe application."""

import os

import psycopg2
from psycopg2 import sql


DATABASE_URL = os.getenv("DATABASE_URL")


def connect():
    """Connect to the PostgreSQL database using DATABASE_URL."""
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured.")
    return psycopg2.connect(DATABASE_URL)


def safe_limit(n, default=10, minimum=1, maximum=100):
    """Safely limit a number to a specified range."""
    try:
        n = int(n)
    except (TypeError, ValueError):
        n = default
    return max(minimum, min(n, maximum))


def run_query(cur, title, query, params=None):
    """Execute a query and print its results."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    cur.execute(query, params or ())
    results = cur.fetchall()

    for row in results:
        print(row)

    return results


def get_analysis():
    """Return all analysis results for the Flask application."""
    conn = connect()
    cur = conn.cursor()

    try:
        q1 = run_query(
            cur,
            "1. Total Fall 2026 applications",
            sql.SQL("""
                SELECT COUNT(*)
                FROM applicants
                WHERE term = %s
                LIMIT %s
            """),
            ("Fall 2026", safe_limit(1)),
        )

        q2 = run_query(
            cur,
            "2. % International Students",
            sql.SQL("""
                SELECT ROUND(
                    100.0 * SUM(
                        CASE
                            WHEN LOWER(COALESCE(us_or_international, ''))
                            LIKE %s
                            THEN 1
                            ELSE 0
                        END
                    ) / NULLIF(COUNT(*), 0),
                    2
                )
                FROM applicants
                LIMIT %s
            """),
            ("%international%", safe_limit(1)),
        )

        q3 = run_query(
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

        q4 = run_query(
            cur,
            "4. GPA of American Students (Fall 2026)",
            sql.SQL("""
                SELECT ROUND(AVG(gpa)::numeric, 2)
                FROM applicants
                WHERE term = %s
                AND gpa IS NOT NULL
                AND (
                    LOWER(us_or_international) LIKE %s
                    OR LOWER(us_or_international) LIKE %s
                    OR LOWER(us_or_international) LIKE %s
                    OR LOWER(us_or_international) LIKE %s
                )
                LIMIT %s
            """),
            (
                "Fall 2026",
                "%american%",
                "%us%",
                "%domestic%",
                "%usa%",
                safe_limit(1),
            ),
        )

        q5 = run_query(
            cur,
            "5. Percentage of Acceptances (Fall 2026)",
            sql.SQL("""
                SELECT ROUND(
                    100.0 * SUM(
                        CASE
                            WHEN status ILIKE %s
                            THEN 1
                            ELSE 0
                        END
                    ) / NULLIF(COUNT(*), 0),
                    2
                )
                FROM applicants
                WHERE term = %s
                LIMIT %s
            """),
            ("%accept%", "Fall 2026", safe_limit(1)),
        )

        q6 = run_query(
            cur,
            "6. GPA of Accepted Students",
            sql.SQL("""
                SELECT ROUND(AVG(gpa)::numeric, 2)
                FROM applicants
                WHERE status ILIKE %s
                AND term = %s
                LIMIT %s
            """),
            ("%accept%", "Fall 2026", safe_limit(1)),
        )

        q7 = run_query(
            cur,
            "7. JHU MS Computer Science Applicants",
            sql.SQL("""
                SELECT COUNT(*)
                FROM applicants
                WHERE LOWER(llm_generated_university) LIKE %s
                AND LOWER(llm_generated_program) LIKE %s
                AND (
                    llm_generated_program ILIKE %s
                    OR llm_generated_program ILIKE %s
                    OR llm_generated_program ILIKE %s
                )
                LIMIT %s
            """),
            (
                "%johns hopkins%",
                "%computer%",
                "%MS%",
                "%M.S%",
                "%Masters%",
                safe_limit(1),
            ),
        )

        q8 = run_query(
            cur,
            "8. PhD Acceptances",
            sql.SQL("""
                SELECT COUNT(*)
                FROM applicants
                WHERE status ILIKE %s
                AND term = %s
                AND (
                    llm_generated_program ILIKE %s
                    OR program ILIKE %s
                )
                LIMIT %s
            """),
            (
                "%accept%",
                "Fall 2026",
                "%PhD%",
                "%PhD%",
                safe_limit(1),
            ),
        )

        q9 = run_query(
            cur,
            "9. LLM Comparison",
            sql.SQL("""
                SELECT
                    COUNT(*) FILTER (
                        WHERE llm_generated_program IS NOT NULL
                    ),
                    COUNT(*) FILTER (
                        WHERE llm_generated_university IS NOT NULL
                    )
                FROM applicants
                LIMIT %s
            """),
            (safe_limit(1),),
        )

        q10 = run_query(
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

        q11 = run_query(
            cur,
            "11. Top programs",
            sql.SQL("""
                SELECT
                    program,
                    COUNT(*) AS total
                FROM applicants
                GROUP BY program
                ORDER BY total DESC
                LIMIT %s
            """),
            (safe_limit(10),),
        )

        return {
            "q1": q1[0][0] if q1 else 0,
            "q2": q2[0][0] if q2 else 0,
            "q3_gpa": q3[0][0] if q3 else None,
            "q3_gre": q3[0][1] if q3 else None,
            "q3_grev": q3[0][2] if q3 else None,
            "q3_aw": q3[0][3] if q3 else None,
            "q4": q4[0][0] if q4 else None,
            "q5": q5[0][0] if q5 else 0,
            "q6": q6[0][0] if q6 else None,
            "q7": q7[0][0] if q7 else 0,
            "q8": q8[0][0] if q8 else 0,
            "q9_programs": q9[0][0] if q9 else 0,
            "q9_universities": q9[0][1] if q9 else 0,
            "q10": q10,
            "q11": q11,
        }

    finally:
        cur.close()
        conn.close()


def query_data():
    """Query the database and print the analysis results."""
    get_analysis()


def main():
    """Run the database analysis."""
    query_data()


if __name__ == "__main__":
    main()
