import pytest

from app import create_app
from app.config import TestConfig
from app.extensions import db


@pytest.fixture
def app():
    """Create a fresh app with an in-memory DB for each test."""
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """Register + log in a user and return an Authorization header."""
    client.post("/api/register", json={"username": "alice", "password": "secret123"})
    resp = client.post("/api/login", json={"username": "alice", "password": "secret123"})
    token = resp.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
