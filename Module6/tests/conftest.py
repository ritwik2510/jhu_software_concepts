"""Test configuration and fixtures."""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/web')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from web.app import create_app


@pytest.fixture
def app():
    """Create test app."""
    test_app = create_app({
        "TESTING": True,
        "DATABASE_URL": os.environ.get(
            "DATABASE_URL",
            "postgresql://myuser:mypassword@localhost:5432/mydatabase"
        )
    })
    return test_app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()