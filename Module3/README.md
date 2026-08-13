# Module 3 - PostgreSQL Data Loading, SQL Analysis, and Flask Dashboard

## Overview
Loads cleaned GradCafe admissions data into PostgreSQL, runs a set of analytical SQL queries, and displays the results on a Flask dashboard.

## Requirements
- Python 3.10+
- PostgreSQL (tested on PostgreSQL 18)

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

3. Create the `gradcafe` database if it doesn't already exist:
```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -c "CREATE DATABASE gradcafe;"
```

4. Create the `applicants` table:
```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d gradcafe -f schema.sql
```

`schema.sql` creates the table with the following schema:

```sql
CREATE TABLE IF NOT EXISTS applicants (
    p_id SERIAL PRIMARY KEY,
    degree TEXT,
    university TEXT,
    program TEXT,
    comments TEXT,
    date_added DATE,
    url TEXT UNIQUE,
    status TEXT,
    term TEXT,
    us_or_international TEXT,
    gpa REAL,
    gre REAL,
    gre_v REAL,
    gre_aw REAL,
    llm_generated_program TEXT,
    llm_generated_university TEXT
);
```

5. Set database credentials as environment variables (optional — defaults to `localhost` / `gradcafe` / `postgres` / `postgres` if unset):
```powershell
$env:DB_HOST = "localhost"
$env:DB_NAME = "gradcafe"
$env:DB_USER = "postgres"
$env:DB_PASSWORD = "your_password"
```

## Loading Data

Requires `applicant_data.json` and `llm_extend_applicant_data.json` from Module 2 (scraping and cleaning) to be present in this folder, or copied over.

```powershell
python load_data.py
```

Inserts are deduplicated on `url` via `ON CONFLICT (url) DO NOTHING`, so the loader can be safely re-run without creating duplicate rows.

## Running Queries

```powershell
python query_data.py
```

Prints the results of 11 analytical queries to the console. See "Query Explanations" below for what each one measures.

## Running the Dashboard

```powershell
python app.py
```

Visit `http://127.0.0.1:5000` in a browser. The dashboard displays the same 11 queries, plus two buttons:
- **Pull New Data** — runs the scraper, cleaner, and loader in sequence, then refreshes the page. This can take several minutes.
- **Update Analysis** — refreshes the page with the latest data already in the database (the queries re-run automatically on every page load).

## Query Explanations

1. **Total Fall 2026 applications** — count of all rows where `term = 'Fall 2026'`.
2. **% international students** — share of all rows where `us_or_international` indicates international status.
3. **Average GPA and GRE scores** — average of each numeric field across all rows with a value (nulls excluded automatically by `AVG()`).
4. **GPA of American students, Fall 2026** — average GPA filtered to Fall 2026 rows with `us_or_international = 'American'`.
5. **% acceptances, Fall 2026** — share of Fall 2026 rows with a status containing "accept".
6. **GPA of accepted students, Fall 2026** — average GPA among Fall 2026 rows with an "accept" status.
7. **JHU MS Computer Science applicants** — count of rows where the standardized university matches Johns Hopkins, the standardized program matches Computer Science, and degree is Masters.
8. **PhD acceptances at MIT/Stanford/CMU/Georgetown, Fall 2026** — count of accepted, Fall 2026, PhD-degree rows at one of the four named universities.
9. **LLM standardization impact** — count of rows where the standardized university/program differs from the originally scraped value, showing how much the standardization step actually changed.
10. **Average GPA by admission status** — GPA averaged and grouped by status (Accepted/Rejected/Waitlisted/etc.).
11. **Top 10 most applied programs** — the 10 program names with the most applications, by raw (unstandardized) program text.

## Known Limitations
- Q11 groups by raw `program` text rather than the standardized version, so minor naming variants of the same program are counted separately.
- Some fields (GPA, GRE scores) are only present when the original poster included them, so averages are computed over a subset of all rows, not the full dataset.