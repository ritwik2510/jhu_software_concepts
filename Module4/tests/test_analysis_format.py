import pytest
import re


@pytest.mark.analysis
def test_answer_label_present(client):

    response = client.get("/analysis")

    html = response.data.decode()

    assert "Answer:" in html


@pytest.mark.analysis
def test_percentage_two_decimals(client):

    response = client.get("/analysis")

    html = response.data.decode()

    matches = re.findall(
        r"\d+\.\d{2}%",
        html
    )

    assert len(matches) > 0