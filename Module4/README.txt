# Module 4 - Testable Flask Application

## Overview
Refactors the GradCafe Flask dashboard into a testable application using an app factory pattern, injectable database configuration, and a pytest suite covering routes, button behavior, database inserts, and end-to-end integration.

## Requirements
- Python 3.10+
- PostgreSQL

## Setup

1. Create and activate a virtual environment:
```powershell
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies:
```powershell
pip install -r requirements.txt
```

3. Create the database and table:
```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -c "CREATE DATABASE gradcafe;"
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d gradcafe -f schema.sql
```

4. Set the database connection string as an environment variable:
```powershell
$env:DATABASE_URL = "postgresql://postgres:postgres@localhost/gradcafe"
```

## Running the App

```powershell
python -m src.app
```

Visit `http://127.0.0.1:5000/analysis` for the dashboard.

## Running Tests

```powershell
python -m pytest -v
```

Tests are organized by marker (`web`, `buttons`, `db`, `integration`) as defined in `pytest.ini`. Database-dependent tests (`db`, `integration`) require a running PostgreSQL instance with `DATABASE_URL` set, and use isolated fake records with unique generated URLs so they don't interfere with real scraped data.

To run a specific category:
```powershell
python -m pytest -m db -v
python -m pytest -m buttons -v
```

## Test Coverage

```powershell
python -m pytest --cov=src --cov-report=term-missing
```

## Application Structure

- `src/app.py`: Flask app factory, routes (`/analysis`, `/pull-data`, `/update-analysis`), and injectable database connection logic
- `src/load_data.py`: loads cleaned applicant data into PostgreSQL, with deduplication via `ON CONFLICT`
- `src/query_data.py`: analytical SQL queries, including `get_analysis_results()` for programmatic access to key statistics
- `src/scrape.py`, `src/clean.py`: scraping and cleaning pipeline from earlier modules
- `tests/`: pytest suite, organized by marker
- `conftest.py`: shared fixtures, including a Flask test client, database connection, and generator for isolated fake test records

## Known Limitations
Full pytest suite covers all core routes, button/busy-state behavior, database inserts (including real dedup and idempotency proof), and end-to-end integration flow. Due to time constraints, unit test coverage was not completed for `clean.py`, `scrape.py`, and portions of `query_data.py`, so the `pytest.ini` coverage requirement of 100% is not currently met.