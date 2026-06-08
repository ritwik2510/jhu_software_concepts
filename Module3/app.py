
from flask import Flask, render_template, request, redirect
import psycopg2
import os

app = Flask(__name__)

conn = psycopg2.connect(
    host="localhost",
    database="gradcafe",
    user="postgres",
    password="postgres"
)

scraping_running = False


def fetch(query):
    cur = conn.cursor()
    cur.execute(query)
    return cur.fetchall()


@app.route("/")
def index():

    q1 = fetch("SELECT COUNT(*) FROM applicants WHERE term='Fall 2026'")
    q2 = fetch("""
        SELECT ROUND(
            100.0 * SUM(CASE WHEN LOWER(us_or_international) LIKE '%international%' THEN 1 ELSE 0 END)
            / COUNT(*), 2)
        FROM applicants;
    """)

    q5 = fetch("""
        SELECT ROUND(
            100.0 * SUM(CASE WHEN status ILIKE '%accept%' THEN 1 ELSE 0 END)
            / COUNT(*), 2)
        FROM applicants
        WHERE term='Fall 2026';
    """)

    return render_template("index.html",
        q1=q1[0][0],
        q2=q2[0][0],
        q5=q5[0][0]
    )


@app.route("/pull", methods=["POST"])
def pull():
    os.system("python load_data.py")
    return redirect("/")


@app.route("/update", methods=["POST"])
def update():
    global scraping_running

    if scraping_running:
        return "Scraping already running..."

    scraping_running = True
    os.system("python query_data.py")
    scraping_running = False

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)