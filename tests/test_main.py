import pytest
from sqlalchemy import text

from app.db.setup_db import get_connection


def test_app_launch(client):
    """
    Test that the application can start and the root endpoint is accessible.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from basic-users!"}


def test_db_connection():
    """
    Explicitly test database connectivity.
    """
    with get_connection() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1
