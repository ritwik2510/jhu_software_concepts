"""Query functions for the Flask dashboard."""
import os
import psycopg2

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://myuser:mypassword@db:5432/mydatabase"
)


def connect():
    """Connects using DATABASE_URL so it works inside Docker."""
    return psycopg2.connect(DATABASE_URL)


def safe_fetch_one(cur, default=0):
    """Safely fetch one row and return first value or default."""
    row = cur.fetchone()
    if row is None or row[0] is None:
        return default
    return row[0]


def get_dashboard_metrics() -> dict:
    """Returns all dashboard numbers as a dictionary for Flask to use."""
    conn = connect()
    cur = conn.cursor()

    try:
        # 1. Total Fall 2026 applications
        cur.execute(
            "SELECT COUNT(*) FROM applicants WHERE term = %s",
            ("Fall 2026",)
        )
        total_applications = safe_fetch_one(cur, 0)

        # 2. % International Students — no %s param so single % is fine
        cur.execute("""
            SELECT ROUND(
                100.0 * SUM(
                    CASE WHEN LOWER(COALESCE(us_or_international,''))
                    LIKE '%international%' THEN 1 ELSE 0 END
                ) / NULLIF(COUNT(*), 0), 2)
            FROM applicants
        """)
        pct_international = safe_fetch_one(cur, 0)

        # 3. Average GPA and GRE scores — no %s param so single % is fine
        cur.execute("""
            SELECT
                ROUND(AVG(gpa::numeric), 2),
                ROUND(AVG(gre::numeric), 2),
                ROUND(AVG(gre_v::numeric), 2),
                ROUND(AVG(gre_aw::numeric), 2)
            FROM applicants
            WHERE gpa IS NOT NULL
        """)
        row = cur.fetchone()
        if row is None:
            avg_gpa, avg_gre, avg_gre_v, avg_gre_aw = 0, 0, 0, 0
        else:
            avg_gpa = row[0] or 0
            avg_gre = row[1] or 0
            avg_gre_v = row[2] or 0
            avg_gre_aw = row[3] or 0

        # 4. GPA of American Students — has %s param so LIKE needs %%
        cur.execute("""
            SELECT ROUND(AVG(gpa::numeric), 2)
            FROM applicants
            WHERE term = %s
            AND gpa IS NOT NULL
            AND (
                LOWER(us_or_international) LIKE '%%american%%'
                OR LOWER(us_or_international) LIKE '%%us%%'
                OR LOWER(us_or_international) LIKE '%%domestic%%'
                OR LOWER(us_or_international) LIKE '%%usa%%'
            )
        """, ("Fall 2026",))
        avg_gpa_american = safe_fetch_one(cur, 0)

        # 5. Percentage of Acceptances — has %s param so LIKE needs %%
        cur.execute("""
            SELECT ROUND(
                100.0 * SUM(CASE WHEN status ILIKE '%%accept%%' THEN 1 ELSE 0 END)
                / NULLIF(COUNT(*), 0), 2)
            FROM applicants
            WHERE term = %s
        """, ("Fall 2026",))
        pct_accepted = safe_fetch_one(cur, 0)

        # 6. GPA of Accepted Students — has %s param so LIKE needs %%
        cur.execute("""
            SELECT ROUND(AVG(gpa::numeric), 2)
            FROM applicants
            WHERE status ILIKE '%%accept%%'
            AND term = %s
            AND gpa IS NOT NULL
        """, ("Fall 2026",))
        avg_gpa_accepted = safe_fetch_one(cur, 0)

        # 7. JHU MS CS Applicants — no %s param so single % is fine
        cur.execute("""
            SELECT COUNT(*)
            FROM applicants
            WHERE LOWER(llm_generated_university) LIKE '%johns hopkins%'
            AND LOWER(llm_generated_program) LIKE '%computer%'
            AND (
                llm_generated_program ILIKE '%MS%'
                OR llm_generated_program ILIKE '%M.S%'
                OR llm_generated_program ILIKE '%Masters%'
            )
        """)
        jhu_ms_cs = safe_fetch_one(cur, 0)

        # 8. PhD Acceptances — has %s param so LIKE needs %%
        cur.execute("""
            SELECT COUNT(*)
            FROM applicants
            WHERE status ILIKE '%%accept%%'
            AND term = %s
            AND (
                llm_generated_program ILIKE '%%PhD%%'
                OR program ILIKE '%%PhD%%'
            )
        """, ("Fall 2026",))
        phd_acceptances = safe_fetch_one(cur, 0)

        # 9. Top programs
        cur.execute("""
            SELECT program, COUNT(*) AS total
            FROM applicants
            GROUP BY program
            ORDER BY total DESC
            LIMIT 10
        """)
        top_programs = cur.fetchall() or []

        # 10. Average GPA by status
        cur.execute("""
            SELECT status, ROUND(AVG(gpa::numeric), 2)
            FROM applicants
            WHERE gpa IS NOT NULL
            GROUP BY status
            ORDER BY AVG(gpa::numeric) DESC
        """)
        gpa_by_status = cur.fetchall() or []

    finally:
        cur.close()
        conn.close()

    return {
        "total_applications": total_applications,
        "pct_international": pct_international,
        "avg_gpa": avg_gpa,
        "avg_gre": avg_gre,
        "avg_gre_v": avg_gre_v,
        "avg_gre_aw": avg_gre_aw,
        "avg_gpa_american": avg_gpa_american,
        "pct_accepted": pct_accepted,
        "avg_gpa_accepted": avg_gpa_accepted,
        "jhu_ms_cs": jhu_ms_cs,
        "phd_acceptances": phd_acceptances,
        "top_programs": top_programs,
        "gpa_by_status": gpa_by_status,
    }