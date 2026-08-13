import pytest
import sys
import os
import uuid
import psycopg2

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.app import create_app


TEST_DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost/gradcafe"
)


@pytest.fixture
def db_url():
    return TEST_DB_URL


@pytest.fixture
def app(db_url):
    flask_app = create_app({
        "TESTING": True,
        "DATABASE_URL": db_url,
    })
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db_conn(db_url):
    conn = psycopg2.connect(db_url)
    yield conn
    conn.close()


@pytest.fixture
def fake_records():
    unique = uuid.uuid4().hex
    return [
        {
            "program": "Test Program A",
            "comments": "test comment",
            "date_added": "2026-01-01",
            "url": f"https://example.com/test-{unique}-1",
            "status": "Accepted",
            "term": "Fall 2026",
            "international": "American",
            "gpa": 3.5,
            "gre": 320,
            "gre_v": 160,
            "gre_aw": 4.5,
            "llm_generated_program": "Test Program A",
            "llm_generated_university": "Test University",
        },
        {
            "program": "Test Program B",
            "comments": None,
            "date_added": "2026-01-02",
            "url": f"https://example.com/test-{unique}-2",
            "status": "Rejected",
            "term": "Fall 2026",
            "international": "International",
            "gpa": 3.2,
            "gre": 310,
            "gre_v": 155,
            "gre_aw": 4.0,
            "llm_generated_program": "Test Program B",
            "llm_generated_university": "Test University",
        },
    ]