import json
from pathlib import Path
from flask import Blueprint, render_template

pages = Blueprint('pages', __name__)


def load_projects():
    data_path = Path(__file__).parent / "data" / "projects.json"
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pages.route("/")
def home():
    return render_template("home.html", active="home")

@pages.route("/contact")
def contact():
    return render_template("contact.html", active="contact")

@pages.route("/projects")
def projects():
    projects_data = load_projects()
    return render_template("projects.html", active="projects", projects=projects_data)