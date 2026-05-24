from app import app
from flask import render_template

@app.route("/")
def home():
    return render_template("home.html", active="home")

@app.route("/contact")
def contact():
    return render_template("contact.html", active="contact")

@app.route("/projects")
def projects():
    return render_template("project.html", active="projects")
