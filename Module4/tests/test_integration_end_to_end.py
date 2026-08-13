import pytest


@pytest.mark.integration
def test_end_to_end(client, monkeypatch, db_conn, db_url, fake_records):
    from src import load_data as load_data_module

    monkeypatch.setattr("src.clean.clean_data", lambda x: x)
    monkeypatch.setattr("src.scrape.scrape_data", lambda *args, **kwargs: fake_records)
    monkeypatch.setattr(
        "src.app.load_data.main",
        lambda *args, **kwargs: load_data_module.load_data(db_url=db_url, data=fake_records)
    )
    monkeypatch.setattr("src.app.query_data.main", lambda *args, **kwargs: None)

    urls = [r["url"] for r in fake_records]
    cur = db_conn.cursor()

    res1 = client.post("/pull-data")
    assert res1.status_code == 200
    assert res1.get_json() == {"ok": True}

    cur.execute("SELECT COUNT(*) FROM applicants WHERE url = ANY(%s);", (urls,))
    inserted_count = cur.fetchone()[0]
    assert inserted_count == len(fake_records)

    res2 = client.post("/update-analysis")
    assert res2.status_code == 200
    assert res2.get_json() == {"ok": True}

    res3 = client.get("/analysis")
    assert res3.status_code == 200

    html = res3.data.decode()
    assert "Answer" in html
    assert "GradCafe Analysis Dashboard" in html

    cur.execute("DELETE FROM applicants WHERE url = ANY(%s);", (urls,))
    db_conn.commit()


@pytest.mark.integration
def test_multiple_pulls_remain_consistent(client, monkeypatch, db_conn, db_url, fake_records):
    from src import load_data as load_data_module

    monkeypatch.setattr(
        "src.app.load_data.main",
        lambda *args, **kwargs: load_data_module.load_data(db_url=db_url, data=fake_records)
    )

    urls = [r["url"] for r in fake_records]
    cur = db_conn.cursor()

    client.post("/pull-data")
    client.post("/pull-data")
    client.post("/pull-data")

    cur.execute("SELECT COUNT(*) FROM applicants WHERE url = ANY(%s);", (urls,))
    count = cur.fetchone()[0]
    assert count == len(fake_records)

    cur.execute("DELETE FROM applicants WHERE url = ANY(%s);", (urls,))
    db_conn.commit()