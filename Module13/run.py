"""Entry point for running the Flask application."""
from src.app import create_app

if __name__ == "__main__":
    create_app().run(debug=True)