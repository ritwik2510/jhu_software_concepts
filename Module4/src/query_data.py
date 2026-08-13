import os
import psycopg2


def get_db_url():
    return os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost/gradcafe")


def connect(db_url=None):
    return psycopg2.connect(db_url or get_db_url())


def run_query(cur, title, query):
    print("\n" + "="*60)
    print(title)
    print("="*60)

    cur.execute(query)
    result = cur.fetchall()

    for row in result:
        print(row)

    return result


def query_data(db_url=None):
    conn = connect(db_url)
    cur = conn.cursor()

    run_query(cur,
        "1. Total Fall 2026 applications",
        """
        SELECT COUNT(*)
        FROM applicants
        WHERE term = 'Fall 2026';
        """
    )

    run_query(cur,
        "2. % International Students",
        """
        SELECT
        ROUND(
            100.0 * SUM(
            CASE
                WHEN LOWER(COALESCE(us_or_international,'')) LIKE '%international%'
                    THEN 1 ELSE 0 END
            ) / COUNT(*), 2)
        FROM applicants;
        """
    )

    run_query(cur,
        "3. Average GPA and GRE scores",
        """
        SELECT
            ROUND(AVG(gpa)::numeric, 2),
            ROUND(AVG(gre)::numeric, 2),
            ROUND(AVG(gre_v)::numeric, 2),
            ROUND(AVG(gre_aw)::numeric, 2)
        FROM applicants
        WHERE gpa IS NOT NULL;
        """
    )

    run_query(cur,
        "4. GPA of American Students (Fall 2026)",
        """
        SELECT ROUND(AVG(gpa)::numeric, 2)
        FROM applicants
        WHERE term = 'Fall 2026'
        AND gpa IS NOT NULL
        AND (
            LOWER(us_or_international) LIKE '%american%'
            OR LOWER(us_or_international) LIKE '%us%'
            OR LOWER(us_or_international) LIKE '%domestic%'
            OR LOWER(us_or_international) LIKE '%usa%'
        );
        """
    )

    run_query(cur,
        "5. Percentage of Acceptances (Fall 2026)",
        """
        SELECT ROUND(
            100.0 * SUM(CASE WHEN status ILIKE '%accept%' THEN 1 ELSE 0 END)
            / COUNT(*), 2)
        FROM applicants
        WHERE term = 'Fall 2026';
        """
    )

    run_query(cur,
        "6. GPA of Accepted Students",
        """
        SELECT ROUND(AVG(gpa)::numeric, 2)
        FROM applicants
        WHERE status ILIKE '%accept%'
        AND term = 'Fall 2026';
        """
    )

    run_query(cur,
        "7. JHU MS Computer Science Applicants",
        """
        SELECT COUNT(*)
        FROM applicants
        WHERE LOWER(llm_generated_university) LIKE '%johns hopkins%'
        AND LOWER(llm_generated_program) LIKE '%computer%'
        AND (
            llm_generated_program ILIKE '%MS%'
            OR llm_generated_program ILIKE '%M.S%'
            OR llm_generated_program ILIKE '%Masters%'
        );
        """
    )

    run_query(cur,
        "8. PhD Acceptances (MIT, Stanford, CMU, Georgetown)",
        """
        SELECT COUNT(*)
        FROM applicants
        WHERE status ILIKE '%accept%'
        AND term = 'Fall 2026'
        AND (
                llm_generated_program ILIKE '%PhD%'
                OR program ILIKE '%PhD%'
            );
        """
    )

    run_query(cur,
        "9. LLM Comparision for Question 8",
        """
        SELECT
            COUNT(*) FILTER (WHERE llm_generated_program IS NOT NULL) AS llm_program_count,
            COUNT(*) FILTER (WHERE llm_generated_university IS NOT NULL) AS llm_university_count
            FROM applicants;
        """
    )

    run_query(cur,
        "10. Average GPA for each admission status",
        """
        SELECT
            status,
            ROUND(AVG(gpa)::numeric, 2) AS avg_gpa
        FROM applicants
        WHERE gpa IS NOT NULL
        GROUP BY status
        ORDER BY avg_gpa DESC;
        """
    )

    run_query(cur,
            "11. Top 10 most applied programs",
            """
            SELECT program, COUNT(*) AS total
            FROM applicants
            GROUP BY program
            ORDER BY total DESC
            LIMIT 10;
            """
    )

    cur.close()
    conn.close()

def get_analysis_results(db_url=None):
    conn = connect(db_url)
    cur = conn.cursor()

    def scalar(query, default=None):
        cur.execute(query)
        row = cur.fetchone()
        if not row or row[0] is None:
            return default
        return row[0]

    results = {
        "total_fall_2026": scalar(
            "SELECT COUNT(*) FROM applicants WHERE term = 'Fall 2026';", 0
        ),
        "pct_international": scalar("""
            SELECT ROUND(
                100.0 * SUM(
                    CASE WHEN LOWER(COALESCE(us_or_international,'')) LIKE '%international%'
                    THEN 1 ELSE 0 END
                ) / NULLIF(COUNT(*), 0), 2)
            FROM applicants;
        """, 0),
        "pct_accepted_fall_2026": scalar("""
            SELECT ROUND(
                100.0 * SUM(CASE WHEN status ILIKE '%accept%' THEN 1 ELSE 0 END)
                / NULLIF(COUNT(*), 0), 2)
            FROM applicants
            WHERE term = 'Fall 2026';
        """, 0),
        "avg_gpa_accepted": scalar("""
            SELECT ROUND(AVG(gpa)::numeric, 2)
            FROM applicants
            WHERE status ILIKE '%accept%'
            AND term = 'Fall 2026';
        """, None),
    }

    cur.close()
    conn.close()
    return results


def main(db_url=None):
    query_data(db_url)


if __name__ == "__main__":
    main()