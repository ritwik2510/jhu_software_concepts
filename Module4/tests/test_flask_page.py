import pytest


@pytest.mark.web
def test_analysis_page_loads(client):
    response = client.get("/analysis")

    assert response.status_code == 200


@pytest.mark.web
def test_page_contains_analysis(client):
    response = client.get("/analysis")

    assert b"Analysis" in response.data


@pytest.mark.web
def test_pull_button_exists(client):
    response = client.get("/analysis")

    assert b"Pull Data" in response.data


@pytest.mark.web
def test_update_button_exists(client):
    response = client.get("/analysis")

    assert b"Update Analysis" in response.data