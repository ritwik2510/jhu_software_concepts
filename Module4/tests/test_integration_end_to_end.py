import src.app as app_module

def test_end_to_end(client, monkeypatch):
    # fake external dependencies
    monkeypatch.setattr("src.clean.clean_data", lambda x: x)
    monkeypatch.setattr("src.scrape.scrape", lambda: [])
    monkeypatch.setattr("src.load_data.load_data", lambda: None)
    monkeypatch.setattr("src.query_data.main", lambda: None)

    # STEP 1: pull data
    res1 = client.post("/pull-data")
    assert res1.status_code in (200, 409)

    # STEP 2: update analysis
    res2 = client.post("/update-analysis")
    assert res2.status_code in (200, 409)

    # STEP 3: render page
    res3 = client.get("/analysis")
    assert res3.status_code == 200

    html = res3.data.decode()
    assert "Analysis" in html
    assert "Answer" in html