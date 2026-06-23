Architecture
============

This system has three layers:

Web Layer (Flask)
-----------------
- app.py handles routes (/analysis, /pull-data, /update-analysis)

ETL Layer
---------
- scrape.py collects raw data
- clean.py processes and normalizes it
- load_data.py inserts into PostgreSQL

Database Layer
--------------
- PostgreSQL stores applicant data
- query_data.py runs analytical queries