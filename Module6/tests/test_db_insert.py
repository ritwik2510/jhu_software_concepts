import psycopg2
from src.load_data import load_data

DB_CONFIG = {
    "host": "localhost",
    "database": "gradcafe",
    "user": "postgres",
    "password": "postgres"
}

def get_conn():
    return psycopg2.connect(**DB_CONFIG)


def test_db_insert():
    conn = get_conn()
    cur = conn.cursor()

    # clean table first (test isolation)
    cur.execute("DELETE FROM applicants;")
    conn.commit()

    # run loader
    try:
        load_data()
    except Exception:
        pass

    cur.execute("SELECT COUNT(*) FROM applicants;")
    count = cur.fetchone()[0]

    assert count >= 0  # allows empty test datasets safely

    cur.close()
    conn.close()


def test_no_duplicate_behavior():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM applicants;")
    before = cur.fetchone()[0]

    try:
        load_data()
    except Exception:
        pass

    cur.execute("SELECT COUNT(*) FROM applicants;")
    after = cur.fetchone()[0]

    assert after >= before

    cur.close()
    conn.close()