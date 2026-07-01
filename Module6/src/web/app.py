"""Flask application for GradCafe applicant analysis."""  # pylint: disable=duplicate-code
import os
import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql
from flask import Flask, render_template, jsonify, current_app
from Module6.src.db import load_data
from Module6.src.worker.etl import query_data

load_dotenv()

SCRAPING_RUNNING = False


def get_connection():
    """Return a psycopg2 database connection or None on failure."""
    try:
        db_url = current_app.config.get("DATABASE_URL")
    except RuntimeError:
        db_url = None

    if not db_url:
        db_url = os.getenv("DATABASE_URL")

    if not db_url:
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        name = os.getenv("DB_NAME", "gradcafe")
        user = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD", "postgres")
        db_url = f"postgresql://{user}:{password}@{host}:{port}/{name}"

    try:
        return psycopg2.connect(db_url)
    except Exception:  # pylint: disable=broad-exception-caught
        return None


def fetch(query, params=None):
    """Execute a query and return all results."""
    conn = get_connection()

    if conn is None:
        return []

    cur = conn.cursor()

    try:
        cur.execute(query, params or ())
        data = cur.fetchall()
    except Exception:  # pylint: disable=broad-exception-caught
        data = []
    finally:
        cur.close()
        conn.close()

    return data


def safe_limit(n, default=10, minimum=1, maximum=100):
    """Clamp n to a safe query limit between minimum and maximum."""
    try:
        n = int(n)
    except (TypeError, ValueError):
        n = default
    return max(minimum, min(n, maximum))


def create_app(test_config=None):
    """Create and configure the Flask application."""
    flask_app = Flask(__name__)

    if test_config:
        flask_app.config.update(test_config)

    @flask_app.route("/analysis")
    def analysis():
        """Render the analysis page."""

        def safe_get(query, params=None, default=None):
            """Fetch a single row or return default."""
            result = fetch(query, params)
            if not result or result[0][0] is None:
                return default
            return result[0]

        q1 = safe_get(
            sql.SQL("SELECT COUNT(*) FROM applicants WHERE term = %s LIMIT %s"),
            ("Fall 2026", safe_limit(1)),
            default=(0,),
        )

        q2 = safe_get(
            sql.SQL("""
                SELECT ROUND(
                    100.0 * SUM(
                        CASE WHEN LOWER(COALESCE(us_or_international,'')) LIKE '%international%'
                        THEN 1 ELSE 0 END
                    ) / NULLIF(COUNT(*),0), 2)
                FROM applicants
                LIMIT %s
            """),
            (safe_limit(1),),
            default=(0,),
        )

        q3 = safe_get(
            sql.SQL("""
                SELECT
                    ROUND(AVG(gpa)::numeric,2),
                    ROUND(AVG(gre)::numeric,2),
                    ROUND(AVG(gre_v)::numeric,2),
                    ROUND(AVG(gre_aw)::numeric,2)
                FROM applicants
                WHERE gpa IS NOT NULL
                LIMIT %s
            """),
            (safe_limit(1),),
            default=(None, None, None, None),
        )

        q4 = safe_get(
            sql.SQL("""
                SELECT ROUND(AVG(gpa)::numeric,2)
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
            default=(None,),
        )

        q5 = safe_get(
            sql.SQL("""
                SELECT ROUND(
                    100.0 * SUM(CASE WHEN status ILIKE '%accept%' THEN 1 ELSE 0 END)
                    / NULLIF(COUNT(*),0),2)
                FROM applicants
                WHERE term = %s
                LIMIT %s
            """),
            ("Fall 2026", safe_limit(1)),
            default=(0,),
        )

        q6 = safe_get(
            sql.SQL("""
                SELECT ROUND(AVG(gpa)::numeric,2)
                FROM applicants
                WHERE status ILIKE '%accept%'
                AND term = %s
                LIMIT %s
            """),
            ("Fall 2026", safe_limit(1)),
            default=(None,),
        )

        q7 = safe_get(
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
            default=(0,),
        )

        q8 = safe_get(
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
            default=(0,),
        )

        q9 = fetch(
            sql.SQL("""
                SELECT
                    COUNT(*) FILTER (WHERE llm_generated_program IS NOT NULL),
                    COUNT(*) FILTER (WHERE llm_generated_university IS NOT NULL)
                FROM applicants
                LIMIT %s
            """),
            (safe_limit(1),),
        ) or [(0, 0)]

        q10 = fetch(
            sql.SQL("""
                SELECT
                    status,
                    ROUND(AVG(gpa)::numeric,2)
                FROM applicants
                WHERE gpa IS NOT NULL
                GROUP BY status
                ORDER BY AVG(gpa) DESC
                LIMIT %s
            """),
            (safe_limit(100),),
        ) or []

        limit = safe_limit(10)

        q11 = fetch(
            sql.SQL("""
                SELECT program, COUNT(*) AS total
                FROM applicants
                GROUP BY program
                ORDER BY total DESC
                LIMIT %s
            """),
            (limit,),
        ) or []

        return render_template(
            "index.html",
            q1=q1[0],
            q2=q2[0],
            q3_gpa=q3[0],
            q3_gre=q3[1],
            q3_grev=q3[2],
            q3_aw=q3[3],
            q4=q4[0],
            q5=q5[0],
            q6=q6[0],
            q7=q7[0],
            q8=q8[0],
            q9_programs=q9[0][0],
            q9_universities=q9[0][1],
            q10=q10,
            q11=q11,
        )

    @flask_app.route("/pull-data", methods=["POST"])
    def pull():
        """Handle pull-data requests."""
        if SCRAPING_RUNNING:
            return jsonify({"busy": True}), 409
        load_data.main()
        return jsonify({"ok": True}), 200

    @flask_app.route("/update-analysis", methods=["POST"])
    def update():
        """Handle update-analysis requests."""
        global SCRAPING_RUNNING  # pylint: disable=global-statement
        if SCRAPING_RUNNING:
            return jsonify({"busy": True}), 409
        SCRAPING_RUNNING = True
        try:
            query_data.main()
        finally:
            SCRAPING_RUNNING = False
        return jsonify({"ok": True}), 200

    return flask_app


if __name__ == "__main__":
    create_app().run(debug=True)
