import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.app import create_app

@pytest.fixture
def app():
    app = create_app({
        "TESTING": True
    })
    return app

@pytest.fixture
def client(app):
    return app.test_client()