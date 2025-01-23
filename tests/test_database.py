from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
import pytest

from src.database.db_setup import setup_database, get_session

def test_setup_database():
    with patch("src.database.db_setup.create_engine") as mock_create_engine:
        setup_database()
        mock_create_engine.assert_called_once_with("sqlite:///transactions.db")

def test_get_session():
    mock_engine = MagicMock()
    
    with patch("src.database.db_setup.sessionmaker") as mock_sessionmaker:
        mock_session = MagicMock(spec=Session)
        mock_sessionmaker.return_value.return_value = mock_session

        # Call the function
        session = get_session(mock_engine)

        # Assert sessionmaker was called with the correct bind
        mock_sessionmaker.assert_called_once_with(bind=mock_engine)

        # Assert the returned session is the mocked session
        assert session == mock_session