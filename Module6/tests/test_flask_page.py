def test_app_factory_exists():
    from Module6.src.web.app import create_app
    app = create_app({"TESTING": True})
    assert app is not None


def test_get_analysis_page(client):
    res = client.get("/analysis")
    assert res.status_code == 200

    html = res.data.decode()

    assert "Analysis" in html
    assert "Answer" in html
    assert "Pull Data" in html
    assert "Update Analysis" in html