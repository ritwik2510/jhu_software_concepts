# Module 2 - GradCafe Scraper and Data Cleaning

## Overview
Scrapes graduate admissions results from TheGradCafe, then cleans and standardizes the raw data into a structured JSON file.

## Setup

1. Create and activate a virtual environment:
```powershell
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies:
```powershell
pip install beautifulsoup4 requests selenium
```

3. Make sure Chrome is installed (Selenium uses `webdriver.Chrome()` directly, no separate driver download needed with recent Selenium versions).

## Running the Scraper

```powershell
python scrape.py
```

This scrapes TheGradCafe's public survey results pages and saves raw entries to `applicant_data.json`. The scraper checkpoints its progress every 200 records in case of an interruption. By default it scrapes 1000 pages (roughly 20000 entries); adjust `max_pages` in `scrape.py` to scrape more or fewer.

## Running the Cleaner

```powershell
python clean.py
```

Reads `applicant_data.json` and produces `llm_extend_applicant_data.json` with:
- Parsed numeric fields (`gpa`, `gre`, `gre_v`, `gre_aw`)
- Normalized `status` values (Accepted / Rejected / Waitlisted / Interview / Unknown)
- Standardized university and program names (`llm_generated_university`, `llm_generated_program`)

## University/Program Standardization

Standardization is rule-based rather than using an external LLM API, for reproducibility. The logic in `_standardize_university` and `_standardize_program`:

- Strips parenthetical notes from university names, e.g. `"University of Toronto (Pissmaster)"` → `"University of Toronto"`
- Strips trailing degree-type suffixes from program names, e.g. `"Business Administration - DBA"` → `"Business Administration"`
- Strips a trailing "online" modifier, e.g. `"Computer Science online"` → `"Computer Science"`

This is not a full canonical mapping (it doesn't merge every naming variant of the same school), but it removes the most common noise patterns seen in the scraped data.

## Known Edge Cases / Limitations

- GPA, GRE, GRE V, and GRE AW are only present in the source data when the original poster chose to include them, so many entries have `null` values for these fields — this reflects real reporting gaps, not a parsing failure.
- Standardization does not catch every university name variant (e.g. abbreviations vs. full names aren't merged), only the most common noise patterns (parentheticals, "online" suffixes, degree-type suffixes).
- `status` values that don't match "accepted," "rejected," "wait," or "interview" are labeled `"Unknown"` rather than guessed.
- Data reflects a snapshot of TheGradCafe's most recent ~150 pages of submissions at time of scraping, not the full historical dataset.