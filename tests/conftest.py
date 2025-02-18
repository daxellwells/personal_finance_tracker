import pytest
from datetime import date
from src.database.models import User

@pytest.fixture
def test_user(test_session):
    """Fixture to create a test user."""
    user = User(username="test_user", email="test@example.com", password="secure123")
    test_session.add(user)
    test_session.commit()
    return user  # Return the created user so tests can use it
