
from flask import Flask, render_template, request, redirect, jsonify
import psycopg2
import os
from src import clean, scrape, query_data, load_data

scraping_running = False

def get_connection():
    try:
        db_url = current_app.config.get("DATABASE_URL")
    except RuntimeError:
        db_url= None

    if not db_url:
        db_url = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost/gradcafe")

    try:
        return psycopg2.connect(db_url)
    except Exception:
        return None

def fetch(query):

    conn = get_connection()
    if conn is None:
        return [(0,0,0,0)]

    cur = conn.cursor()

    cur.execute(query)

    data = cur.fetchall()

    cur.close()
    conn.close()

    return data

def create_app(test_config=None):

    app = Flask(__name__)

    if test_config:
        app.config.update(test_config)


    @app.route("/analysis")
    def analysis():

        def safe_get(query, default=None):
            result = fetch(query)
            if not result or not result[0] or result[0][0] is None:
                return default
            return result[0]

        # --- Queries ---
        q1 = safe_get("""
            SELECT COUNT(*)
            FROM applicants
            WHERE term='Fall 2026';
        """, (0,))

        q2 = safe_get("""
            SELECT ROUND(
                100.0 * SUM(
                    CASE
                        WHEN LOWER(COALESCE(us_or_international,'')) LIKE '%international%'
                        THEN 1 ELSE 0
                    END
                ) / NULLIF(COUNT(*), 0), 2)
            FROM applicants;
        """, (0,))

        q3 = safe_get("""
            SELECT
                ROUND(AVG(gpa)::numeric, 2),
                ROUND(AVG(gre)::numeric, 2),
                ROUND(AVG(gre_v)::numeric, 2),
                ROUND(AVG(gre_aw)::numeric, 2)
            FROM applicants
            WHERE gpa IS NOT NULL;
        """, (None, None, None, None))

        q4 = safe_get("""
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
        """, (None,))

        q5 = safe_get("""
            SELECT ROUND(
                100.0 * SUM(
                    CASE WHEN status ILIKE '%accept%' THEN 1 ELSE 0 END
                ) / NULLIF(COUNT(*), 0), 2)
            FROM applicants
            WHERE term='Fall 2026';
        """, (0,))

        q6 = safe_get("""
            SELECT ROUND(AVG(gpa)::numeric, 2)
            FROM applicants
            WHERE status ILIKE '%accept%'
            AND term='Fall 2026';
        """, (None,))

        q7 = safe_get("""
            SELECT COUNT(*)
            FROM applicants
            WHERE LOWER(llm_generated_university) LIKE '%johns hopkins%'
            AND LOWER(llm_generated_program) LIKE '%computer%'
            AND (
                llm_generated_program ILIKE '%MS%'
                OR llm_generated_program ILIKE '%M.S%'
                OR llm_generated_program ILIKE '%Masters%'
            );
        """, (0,))

        q8 = safe_get("""
            SELECT COUNT(*)
            FROM applicants
            WHERE status ILIKE '%accept%'
            AND term='Fall 2026'
            AND (
                llm_generated_program ILIKE '%PhD%'
                OR program ILIKE '%PhD%'
            );
        """, (0,))

        q9 = fetch("""
            SELECT
                COUNT(*) FILTER (WHERE llm_generated_program IS NOT NULL),
                COUNT(*) FILTER (WHERE llm_generated_university IS NOT NULL)
            FROM applicants;
        """)

        q9_programs = q9[0][0] if q9 else 0
        q9_universities = q9[0][1] if q9 else 0

        q10 = fetch("""
            SELECT
                status,
                ROUND(AVG(gpa)::numeric, 2)
            FROM applicants
            WHERE gpa IS NOT NULL
            GROUP BY status
            ORDER BY AVG(gpa) DESC;
        """) or []

        q11 = fetch("""
            SELECT program, COUNT(*) AS total
            FROM applicants
            GROUP BY program
            ORDER BY total DESC
            LIMIT 10;
        """) or []

        # --- Render safely ---
        return render_template(
            "index.html",

            q1=q1[0] if q1 and q1[0] is not None else 0,
            q2=q2[0] if q2 and q2[0] is not None else 0,

            q3_gpa=q3[0] if q3 else None,
            q3_gre=q3[1] if q3 else None,
            q3_grev=q3[2] if q3 else None,
            q3_aw=q3[3] if q3 else None,

            q4=q4[0] if q4 else None,
            q5=q5[0] if q5 else 0,
            q6=q6[0] if q6 else None,
            q7=q7[0] if q7 else 0,
            q8=q8[0] if q8 else 0,

            q9_programs=q9_programs,
            q9_universities=q9_universities,

            q10=q10,
            q11=q11
        )
    
    
    @app.route("/pull-data", methods=["POST"])
    def pull():
        global scraping_running

        if scraping_running:
            return jsonify({"busy": True}), 409

        load_data.main()
        return jsonify({"ok": True}), 200
        

    @app.route("/update-analysis", methods=["POST"])
    def update():
        global scraping_running

        if scraping_running:
            return jsonify({"busy": True}), 409

        scraping_running = True
        try:
            query_data.main()
        finally:
            scraping_running = False

        return jsonify({"ok": True}), 200

    return app

app = create_app()


if __name__ == "__main__":
    app.run(debug=True)