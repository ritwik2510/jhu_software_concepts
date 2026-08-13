from flask import Flask, render_template, request, redirect
import psycopg2
import os
import subprocess

app = Flask(__name__)

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "database": os.environ.get("DB_NAME", "gradcafe"),
    "user": os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", "postgres")
}

conn = psycopg2.connect(**DB_CONFIG)

scraping_running = False


def fetch(query):
    cur = conn.cursor()
    cur.execute(query)
    return cur.fetchall()


@app.route("/")
def index():

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
        FROM applicants;
    """)

    q4 = fetch("""
        SELECT ROUND(AVG(gpa)::numeric, 2)
        FROM applicants
        WHERE term = 'Fall 2026'
        AND gpa IS NOT NULL
        AND us_or_international = 'American';
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
        WHERE llm_generated_university ILIKE '%Johns Hopkins%'
        AND llm_generated_program ILIKE '%Computer Science%'
        AND degree = 'Masters';
    """)

    q8 = fetch("""
        SELECT COUNT(*)
        FROM applicants
        WHERE status ILIKE '%accept%'
        AND term='Fall 2026'
        AND degree = 'PhD'
        AND (
            llm_generated_university ILIKE '%Georgetown%'
            OR llm_generated_university ILIKE '%MIT%'
            OR llm_generated_university ILIKE '%Massachusetts Institute of Technology%'
            OR llm_generated_university ILIKE '%Stanford%'
            OR llm_generated_university ILIKE '%Carnegie Mellon%'
            OR llm_generated_university ILIKE '%CMU%'
        );
    """)

    q9 = fetch("""
        SELECT
            COUNT(*) FILTER (
                WHERE university IS DISTINCT FROM llm_generated_university
            ),
            COUNT(*) FILTER (
                WHERE program IS DISTINCT FROM llm_generated_program
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


@app.route("/pull", methods=["POST"])
def pull():
    global scraping_running

    if scraping_running:
        return "A scrape is already in progress. Please wait for it to finish before starting another."

    scraping_running = True
    try:
        subprocess.run(["python", "scrape.py"], check=True)
        subprocess.run(["python", "clean.py"], check=True)
        subprocess.run(["python", "load_data.py"], check=True)
    finally:
        scraping_running = False

    return redirect("/")


@app.route("/update", methods=["POST"])
def update():
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)