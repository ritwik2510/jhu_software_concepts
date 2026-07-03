"""Flask entrypoint."""
from flask import Flask, jsonify, render_template
from publisher import publish_task
from query_data import get_dashboard_metrics

app = Flask(__name__)


@app.route("/")
def home():
    """Render the main dashboard."""
    data = get_dashboard_metrics()
    return render_template(
        "index.html",
        q1=data["total_applications"],
        q2=data["pct_international"],
        q3_gpa=data["avg_gpa"],
        q3_gre=data["avg_gre"],
        q3_grev=data["avg_gre_v"],
        q3_aw=data["avg_gre_aw"],
        q4=data["avg_gpa_american"],
        q5=data["pct_accepted"],
        q6=data["avg_gpa_accepted"],
        q7=data["jhu_ms_cs"],
        q8=data["phd_acceptances"],
        q9_programs=data["top_programs"],
        q9_universities=data["gpa_by_status"],
        q10=data["gpa_by_status"],
        q11=data["top_programs"],
    )


@app.route("/tasks/scrape", methods=["POST"])
def scrape_new_data():
    """Queue a scrape task."""
    try:
        publish_task("scrape_new_data")
    except Exception:  # pylint: disable=broad-exception-caught
        return jsonify({"status": "error", "message": "queue unavailable"}), 503
    return jsonify({"status": "queued", "message": "request queued"}), 202


@app.route("/tasks/recompute", methods=["POST"])
def recompute_analytics():
    """Queue a recompute task."""
    try:
        publish_task("recompute_analytics")
    except Exception:  # pylint: disable=broad-exception-caught
        return jsonify({"status": "error", "message": "queue unavailable"}), 503
    return jsonify({"status": "queued", "message": "request queued"}), 202


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)