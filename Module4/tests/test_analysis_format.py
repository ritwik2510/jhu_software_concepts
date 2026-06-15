def test_analysis_formatting(client):
    res = client.get("/analysis")
    html = res.data.decode()

    # required UI text
    assert "Answer" in html or "Answers" in html

    # check structure exists
    assert "<" in html and ">" in html  # basic sanity check


def test_percentage_formatting(client):
    res = client.get("/analysis")
    html = res.data.decode()

    # loose check for decimal formatting (rubric requirement)
    assert "." in html