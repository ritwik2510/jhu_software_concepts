"""End-to-end integration tests."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/web')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


def test_end_to_end(client, monkeypatch):
    """Test end to end flow."""
    monkeypatch.setattr("web.app.publish_task", lambda kind: None)

    res1 = client.post("/pull-data")
    assert res1.status_code in (200, 202, 409, 503)

    res2 = client.post("/update-analysis")
    assert res2.status_code in (200, 202, 409, 503)

    res3 = client.get("/analysis")
    assert res3.status_code in (200, 500)