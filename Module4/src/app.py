
from flask import Flask, render_template, request, redirect, jsonify
import psycopg2
import os

scraping_running = False

def get_connection():
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresq1://postgres:postgres@localhost/gradcafe"
    )


    return psycopg2.connect(database_url)

def fetch(query):

    conn = get_connection()

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

        q1 = fetch("""
            SELECT COUNT(*)
            FROM applicants
            WHERE term='Fall 2026';
        """)

        q2 = fetch("""
            SELECT ROUND(
                100.0 * SUM(
                    CASE
                        WHEN LOWER(COALESCE(us_or_international,'')) LIKE '%international%'
                        THEN 1 ELSE 0
                    END
                ) / COUNT(*), 2)
            FROM applicants;
        """)

        q3 = fetch("""
            SELECT
                ROUND(AVG(gpa)::numeric, 2),
                ROUND(AVG(gre)::numeric, 2),
                ROUND(AVG(gre_v)::numeric, 2),
                ROUND(AVG(gre_aw)::numeric, 2)
            FROM applicants
            WHERE gpa IS NOT NULL;
        """)

        q4 = fetch("""
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
        """)

        q5 = fetch("""
            SELECT ROUND(
                100.0 * SUM(
                    CASE WHEN status ILIKE '%accept%' THEN 1 ELSE 0 END
                ) / COUNT(*), 2)
            FROM applicants
            WHERE term='Fall 2026';
        """)

        q6 = fetch("""
            SELECT ROUND(AVG(gpa)::numeric, 2)
            FROM applicants
            WHERE status ILIKE '%accept%'
            AND term='Fall 2026';
        """)

        q7 = fetch("""
            SELECT COUNT(*)
            FROM applicants
            WHERE LOWER(llm_generated_university) LIKE '%johns hopkins%'
            AND LOWER(llm_generated_program) LIKE '%computer%'
            AND (
                llm_generated_program ILIKE '%MS%'
                OR llm_generated_program ILIKE '%M.S%'
                OR llm_generated_program ILIKE '%Masters%'
            );
        """)

        q8 = fetch("""
            SELECT COUNT(*)
            FROM applicants
            WHERE status ILIKE '%accept%'
            AND term='Fall 2026'
            AND (
                llm_generated_program ILIKE '%PhD%'
                OR program ILIKE '%PhD%'
            );
        """)

        q9 = fetch("""
            SELECT
                COUNT(*) FILTER (
                    WHERE llm_generated_program IS NOT NULL
                ),
                COUNT(*) FILTER (
                    WHERE llm_generated_university IS NOT NULL
                )
            FROM applicants;
        """)

        q10 = fetch("""
            SELECT
                status,
                ROUND(AVG(gpa)::numeric, 2)
            FROM applicants
            WHERE gpa IS NOT NULL
            GROUP BY status
            ORDER BY AVG(gpa) DESC;
        """)

        q11 = fetch("""
            SELECT program, COUNT(*) AS total
            FROM applicants
            GROUP BY program
            ORDER BY total DESC
            LIMIT 10;
        """)

        return render_template(
            "index.html",

            q1=q1[0][0],
            q2=q2[0][0],

            q3_gpa=q3[0][0],
            q3_gre=q3[0][1],
            q3_grev=q3[0][2],
            q3_aw=q3[0][3],

            q4=q4[0][0],
            q5=q5[0][0],
            q6=q6[0][0],
            q7=q7[0][0],
            q8=q8[0][0],

            q9_programs=q9[0][0],
            q9_universities=q9[0][1],

            q10=q10,
            q11=q11
        )
    @app.route("/pull-data", methods=["POST"])
    def pull():
        global scraping_running

        if scraping_running:
            return jsonify({"busy": True}), 409
        
        os.system("python load_data.py")

        return jsonify({"ok": True}), 200
        

    @app.route("/update-analysis", methods=["POST"])
    def update():
        global scraping_running

        if scraping_running:
            return jsonify({"busy": True}), 409
        
        scraping_running = True

        try:
            os.system("python query_data.py")
        finally:
            scraping_running = False
        return jsonify({"ok": True}), 200

    return app

app = create_app()


if __name__ == "__main__":
    app.run(debug=True)