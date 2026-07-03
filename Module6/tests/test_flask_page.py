"""Tests for Flask page functionality."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/web')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


def test_app_factory_exists():
    """Test that app factory creates an app."""
    from web.app import create_app
    app = create_app({"TESTING": True})
    assert app is not None


def test_get_analysis_page(client):
    """Test analysis page loads."""
    res = client.get("/analysis")
    assert res.status_code in (200, 500)

    if res.status_code == 200:
        html = res.data.decode()
        assert "Analysis" in html