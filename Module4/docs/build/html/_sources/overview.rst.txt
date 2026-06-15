Overview & Setup
================

This project is a Flask + PostgreSQL pipeline that scrapes GradCafe data and provides analysis.

Setup Instructions
------------------

1. Install dependencies:

   pip install -r requirements.txt

2. Set environment variables:

   DATABASE_URL=postgresql://postgres:postgres@localhost/gradcafe

3. Run the Flask app:

   python -m src.app

4. Run tests:

   pytest --cov=src