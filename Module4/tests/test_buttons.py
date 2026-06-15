import pytest
from unittest.mock import MagicMock
import src.app as app_module
import src.scrape

FAKE_SURVEY_HTML = """
<table>
    <tr>
        <td>MIT</td>
        <td>Computer Science PhD</td>
        <td>Dec 15</td>
        <td>Accepted via Email</td>
        <td><a href="/survey/detail/123">View</a></td>
    </tr>
    <tr><td>Too Few Cells</td></tr>
</table>
"""
FAKE_DETAIL_HTML = "<html><p>Simulated comment</p></html>"


@pytest.fixture
def client():
    app = app_module.create_app({"TESTING": True, "DATABASE_URL": "postgresql://fake:fake@localhost/fake"})
    with app.test_client() as client:
        yield client


@pytest.mark.buttons
def test_pull_data_ok(client, monkeypatch):
    app_module.scraping_running = False
    monkeypatch.setattr("src.load_data.main", lambda: None)

    res = client.post("/pull-data")
    assert res.status_code == 200
    assert res.json == {"ok": True}


@pytest.mark.buttons
def test_update_analysis_ok(client, monkeypatch):
    app_module.scraping_running = False
    monkeypatch.setattr("src.query_data.main", lambda: None)

    res = client.post("/update-analysis")
    assert res.status_code == 200
    assert res.json == {"ok": True}


@pytest.mark.buttons
def test_busy_state(client, monkeypatch):
    app_module.scraping_running = True
    try:
        res1 = client.post("/pull-data")
        res2 = client.post("/update-analysis")

        assert res1.status_code == 409
        assert res1.json == {"busy": True}
        assert res2.status_code == 409
        assert res2.json == {"busy": True}
    finally:
        app_module.scraping_running = False


@pytest.mark.buttons
def test_scrape_engine_lifecycle(monkeypatch, tmp_path):
    mock_driver = MagicMock()
    mock_driver.page_source = FAKE_SURVEY_HTML
    monkeypatch.setattr("src.scrape.get_driver", lambda: mock_driver)

    mock_response = MagicMock()
    mock_response.text = FAKE_DETAIL_HTML
    monkeypatch.setattr("src.scrape.session.get", lambda url, timeout: mock_response)

    records = src.scrape.scrape_data(pages_to_run=[1])
    assert len(records) == 1
    assert records[0]["university"] == "MIT"

    monkeypatch.setattr("src.scrape.session.get", lambda *a, **kw: Exception("Error"))
    failed_details = src.scrape.parse_detail("https://invalid-url.com")
    assert failed_details["comments"] is None

    temp_file = tmp_path / "test_output.json"
    src.scrape.save_data(records, filename=str(temp_file))
    assert temp_file.exists()

    monkeypatch.setattr("src.scrape.scrape_data", lambda: [{"ok": True}])
    assert src.scrape.main() == [{"ok": True}]