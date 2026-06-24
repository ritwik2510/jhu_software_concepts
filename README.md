# jhu_software_concepts

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your values. Never commit `.env`.

| Variable | Description | Default |
|---|---|---|
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `DB_NAME` | Database name | `gradcafe` |
| `DB_USER` | DB user | `postgres` |
| `DB_PASSWORD` | DB password | — |
| `DATABASE_URL` | Optional full DSN | — |

---

## Fresh Install — pip + venv

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
copy .env.example .env
flask --app src.app run
```

---

## Fresh Install — uv

```powershell
pip install uv
uv venv
.venv\Scripts\activate
uv pip sync requirements.txt
uv pip install -e .
copy .env.example .env
flask --app src.app run
```

---

## Running Pylint

```powershell
.venv\Scripts\python.exe -m pylint src/ --fail-under=10
```

Required score: 10.00/10 on all files under `src/`.

---

## Running Tests

```powershell
.venv\Scripts\python.exe -m pytest tests/ -v
```

---

## Generating the Dependency Graph

Install Graphviz from https://graphviz.org/download/ and check "Add to PATH" during install. Then:

```powershell
python -m pydeps src/app.py --noshow -T svg -o dependency.svg
```

---

## Snyk Security Scan

```powershell
snyk auth
snyk test
```

---

## Least-Privilege Database Setup

```sql
CREATE USER gradcafe_app WITH PASSWORD 'your_password';
GRANT CONNECT ON DATABASE gradcafe TO gradcafe_app;
GRANT USAGE ON SCHEMA public TO gradcafe_app;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO gradcafe_app;
```

Set `DB_USER=gradcafe_app` and `DB_PASSWORD=your_password` in your `.env`.

---

## GitHub Actions CI

The workflow in `.github/workflows/ci.yml` runs on every push and pull request with four jobs:

1. **Pylint** — fails if score is below 10.00/10
2. **Dependency graph** — generates and validates `dependency.svg`
3. **Snyk** — scans `requirements.txt` for vulnerabilities
4. **Pytest** — runs the full test suite and fails on any failure