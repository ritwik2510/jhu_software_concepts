import pytest


@pytest.mark.buttons
def test_pull_data_returns_ok_when_not_busy(client, monkeypatch):
    monkeypatch.setattr("src.app.load_data.main", lambda *args, **kwargs: None)

    res = client.post("/pull-data")

    assert res.status_code == 200
    assert res.get_json() == {"ok": True}


@pytest.mark.buttons
def test_update_analysis_returns_ok_when_not_busy(client, monkeypatch):
    monkeypatch.setattr("src.app.query_data.main", lambda *args, **kwargs: None)

    res = client.post("/update-analysis")

    assert res.status_code == 200
    assert res.get_json() == {"ok": True}


@pytest.mark.buttons
def test_pull_data_returns_409_when_busy(client):
    client.application.state["scraping_running"] = True

    res = client.post("/pull-data")

    assert res.status_code == 409
    assert res.get_json() == {"busy": True}

    client.application.state["scraping_running"] = False


@pytest.mark.buttons
def test_update_analysis_returns_409_when_busy(client):
    client.application.state["scraping_running"] = True

    res = client.post("/update-analysis")

    assert res.status_code == 409
    assert res.get_json() == {"busy": True}

    client.application.state["scraping_running"] = False


@pytest.mark.buttons
def test_busy_update_performs_no_update(client, monkeypatch):
    was_called = {"called": False}

    def fake_main(*args, **kwargs):
        was_called["called"] = True

    monkeypatch.setattr("src.app.query_data.main", fake_main)

    client.application.state["scraping_running"] = True
    res = client.post("/update-analysis")

    assert res.status_code == 409
    assert was_called["called"] is False

    client.application.state["scraping_running"] = False