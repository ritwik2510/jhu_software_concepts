import pytest
from src.load_data import load_data


@pytest.mark.db
def test_db_insert_creates_new_rows(db_conn, db_url, fake_records):
    cur = db_conn.cursor()

    urls = [r["url"] for r in fake_records]

    cur.execute("SELECT COUNT(*) FROM applicants WHERE url = ANY(%s);", (urls,))
    before = cur.fetchone()[0]
    assert before == 0

    result = load_data(db_url=db_url, data=fake_records)

    cur.execute("SELECT COUNT(*) FROM applicants WHERE url = ANY(%s);", (urls,))
    after = cur.fetchone()[0]

    assert after == len(fake_records)
    assert result["inserted"] == len(fake_records)
    assert result["skipped"] == 0

    cur.execute("DELETE FROM applicants WHERE url = ANY(%s);", (urls,))
    db_conn.commit()


@pytest.mark.db
def test_db_insert_required_fields_not_null(db_conn, db_url, fake_records):
    cur = db_conn.cursor()
    urls = [r["url"] for r in fake_records]

    load_data(db_url=db_url, data=fake_records)

    cur.execute(
        "SELECT program, status, term, url FROM applicants WHERE url = ANY(%s);",
        (urls,)
    )
    rows = cur.fetchall()

    assert len(rows) == len(fake_records)
    for row in rows:
        for value in row:
            assert value is not None

    cur.execute("DELETE FROM applicants WHERE url = ANY(%s);", (urls,))
    db_conn.commit()


@pytest.mark.db
def test_db_insert_is_idempotent(db_conn, db_url, fake_records):
    cur = db_conn.cursor()
    urls = [r["url"] for r in fake_records]

    first_result = load_data(db_url=db_url, data=fake_records)
    assert first_result["inserted"] == len(fake_records)

    second_result = load_data(db_url=db_url, data=fake_records)
    assert second_result["inserted"] == 0
    assert second_result["skipped"] == len(fake_records)

    cur.execute("SELECT COUNT(*) FROM applicants WHERE url = ANY(%s);", (urls,))
    count = cur.fetchone()[0]
    assert count == len(fake_records)

    cur.execute("DELETE FROM applicants WHERE url = ANY(%s);", (urls,))
    db_conn.commit()