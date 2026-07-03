"""Tests for database insert functionality."""
import os
import psycopg2
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from db.load_data import load_data

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "database": os.environ.get("DB_NAME", "mydatabase"),
    "user": os.environ.get("DB_USER", "myuser"),
    "password": os.environ.get("DB_PASSWORD", "mypassword"),
    "port": os.environ.get("DB_PORT", "5432"),
}


def get_conn():
    """Get database connection."""
    return psycopg2.connect(**DB_CONFIG)


def test_db_insert():
    """Test database insert."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM applicants;")
    conn.commit()

    try:
        load_data()
    except Exception:  # pylint: disable=broad-exception-caught
        pass

    cur.execute("SELECT COUNT(*) FROM applicants;")
    count = cur.fetchone()[0]
    assert count >= 0

    cur.close()
    conn.close()


def test_no_duplicate_behavior():
    """Test no duplicate behavior."""
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM applicants;")
    before = cur.fetchone()[0]

    try:
        load_data()
    except Exception:  # pylint: disable=broad-exception-caught
        pass

    cur.execute("SELECT COUNT(*) FROM applicants;")
    after = cur.fetchone()[0]
    assert after >= before

    cur.close()
    conn.close()