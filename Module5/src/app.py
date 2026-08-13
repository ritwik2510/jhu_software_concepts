"""Flask application for GradCafe applicant analysis."""

import os

import psycopg2
from flask import Flask, jsonify, render_template
from psycopg2 import Error as PsycopgError

from src import load_data, query_data


def get_connection():
    """Return a PostgreSQL database connection."""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        return None

    try:
        return psycopg2.connect(database_url)
    except PsycopgError:
        return None


def create_app(test_config=None):
    """Create and configure the Flask application."""
    flask_app = Flask(__name__)

    if test_config:
        flask_app.config.update(test_config)

    state = {"scraping_running": False}

    @flask_app.route("/analysis")
    def analysis():
        """Render the analysis page."""
        results = query_data.get_analysis()

        return render_template(
            "index.html",
            q1=results["q1"],
            q2=results["q2"],
            q3_gpa=results["q3_gpa"],
            q3_gre=results["q3_gre"],
            q3_grev=results["q3_grev"],
            q3_aw=results["q3_aw"],
            q4=results["q4"],
            q5=results["q5"],
            q6=results["q6"],
            q7=results["q7"],
            q8=results["q8"],
            q9_programs=results["q9_programs"],
            q9_universities=results["q9_universities"],
            q10=results["q10"],
            q11=results["q11"],
        )

    @flask_app.route("/pull-data", methods=["POST"])
    def pull():
        """Handle pull-data requests."""
        if state["scraping_running"]:
            return jsonify({"busy": True}), 409

        load_data.main()
        return jsonify({"ok": True}), 200

    @flask_app.route("/update-analysis", methods=["POST"])
    def update():
        """Handle update-analysis requests."""
        if state["scraping_running"]:
            return jsonify({"busy": True}), 409

        state["scraping_running"] = True

        try:
            query_data.main()
        finally:
            state["scraping_running"] = False

        return jsonify({"ok": True}), 200

    return flask_app


if __name__ == "__main__":
    create_app().run(debug=True)