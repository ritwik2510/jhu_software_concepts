import pytest


@pytest.mark.web
def test_app_factory_exists():
    from src.app import create_app
    app = create_app({"TESTING": True})
    assert app is not None


@pytest.mark.web
def test_get_analysis_page(client):
    res = client.get("/analysis")
    assert res.status_code == 200

    html = res.data.decode()

    assert "Analysis" in html or "GradCafe Analysis Dashboard" in html
    assert "Answer" in html
    assert "Pull Data" in html
    assert "Update Analysis" in html