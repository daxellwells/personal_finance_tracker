from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session, sessionmaker
from src.database.models import Base, User, Budget, Transaction, CATEGORIES
from src.services.db_operations import create_transaction, create_user, create_budget
from datetime import date
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

@pytest.fixture(scope="function") # resets test session for each function
def test_session():
    # creates in-memory SQLite db for testing
    engine = create_engine("sqlite:///:memory:") #temp db
    Base.metadata.create_all(engine) # Create tables
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

def test_create_transaction(test_session, test_user):
    # ensure transactions are correctly created and linked to a user
    transaction = Transaction(user=test_user, amount=-50.0, category="Food", date=date(2020, 5, 26))
    test_session.add(transaction)
    test_session.commit()
    fetched_user = test_session.query(User).filter_by(username="test_user").first()
    assert len(fetched_user.transactions) == 1
    assert fetched_user.transactions[0].category == "Food"

def test_create_transaction_function(test_session, test_user):
    transaction = create_transaction(test_session, user_id=test_user.id, amount=100.0, category="Food", date=date(2025,1,1), description="Test transaction")
    assert isinstance(transaction, Transaction)
    fetched_user = test_session.query(User).filter_by(username="test_user").first()
    assert len(fetched_user.transactions) == 1
    assert fetched_user.transactions[0].category == "Food"
    assert transaction.user_id == test_user.id
    assert transaction.amount == 100.0
    assert transaction.category == "Food"
    assert transaction.date == date(2025,1,1)
    assert transaction.description == "Test transaction"
    assert transaction.id == 1

def test_create_budget(test_session, test_user):
    budget = Budget(user_id=test_user.id, category="Food", monthly_budget=1200.0)
    test_session.add(budget)
    test_session.commit()
    fetched_user = test_session.query(User).filter_by(username="test_user").first()
    assert len(fetched_user.budgets) == 1
    assert fetched_user.budgets[0].category == "Food"
    assert fetched_user.budgets[0].monthly_budget == 1200.0

def test_create_budget_function(test_session, test_user):
    budget = create_budget(test_session, user_id=test_user.id, category="Food", monthly_budget=1200.0)
    assert isinstance(budget, Budget)
    fetched_user = test_session.query(User).filter_by(username="test_user").first()
    assert len(fetched_user.budgets) == 1
    assert fetched_user.budgets[0].user_id == test_user.id
    assert fetched_user.budgets[0].category == "Food"
    assert fetched_user.budgets[0].monthly_budget == 1200.0

def test_create_user(test_session):
    user = User(username="test_user", email="test_email@email.com", password="fakepassword")
    test_session.add(user)
    test_session.commit()
    assert isinstance(user, User)
    fetched_user = test_session.query(User).filter_by(username="test_user").first()
    assert fetched_user.id == 1
    assert fetched_user.username == "test_user"
    assert fetched_user.email == "test_email@email.com"
    assert fetched_user.password =="fakepassword"

def test_create_user_function(test_session):
    user = create_user(test_session, username="test_user", email="test_email@email.com", password="fakepassword")
    assert isinstance(user, User)
    fetched_user = test_session.query(User).filter_by(username="test_user").first()
    assert fetched_user.id == 1
    assert fetched_user.username == "test_user"
    assert fetched_user.email == "test_email@email.com"
    assert fetched_user.password =="fakepassword"

def test_tables_exist(test_session):
    # ensure all tables exist in the test db
    inspector = inspect(test_session.bind)
    tables = inspector.get_table_names()
    assert "users" in tables
    assert "transactions" in tables
    assert "budgets" in tables

def test_user_budget_relationship(test_session, test_user):
    test_session.add(test_user)
    test_session.commit()

    budget1 = Budget(user=test_user, category="Food", monthly_budget=300.0)
    budget2 = Budget(user=test_user, category="Entertainment", monthly_budget=100.0)
    test_session.add_all([budget1, budget2])
    test_session.commit()

    fetched_user = test_session.query(User).filter_by(username="test_user").first()
    assert len(fetched_user.budgets) == 2
    
def test_cascade_delete(test_session, test_user):
    # ensure deleting a User also deletes associated budgets and transactions
    transaction = create_transaction(test_session, user_id=test_user.id, amount=-500.0, category="Rent", date=date(2025,2,17), description="Test transaction")
    budget = create_budget(test_session, user_id=test_user.id, category="Rent", monthly_budget=800.0)

    test_session.delete(test_user)
    test_session.commit()

    assert test_session.query(User).count() == 0
    assert test_session.query(Budget).count() == 0
    assert test_session.query(Transaction).count() == 0

def test_unique_username(test_session,test_user):
    # ensure username is uniqe
    user2 = User(username="test_user", email="unique@example.com",password="fakepassword")
    test_session.add(user2)
    with pytest.raises(Exception):
        test_session.commit()

def test_unique_email(test_session,test_user):
    # ensure username email is unique
    user2 = User(username="unique_user", email="test@example.com",password="fakepassword")
    test_session.add(user2)
    with pytest.raises(Exception):
        test_session.commit()

def test_budget_cannot_be_negative(test_session,test_user):
    #budgets cannot have negative limits
    with pytest.raises(ValueError, match="Budget amount must be positive"):
        budget = create_budget(test_session, user_id=test_user.id, category="Entertainment", monthly_budget=-100.0)

def test_transaction_amount_cannot_be_zero(test_session, test_user):
    """Ensure transactions cannot have an amount of zero."""
    with pytest.raises(ValueError, match="Transaction amount cannot be zero"):
        transaction = create_transaction(test_session, user_id=test_user.id, amount=0.0, category="Food", date=date(2025, 1, 1))
        test_session.add(transaction)
        test_session.commit()  # Expect failure

def test_category_validation_budget(test_session, test_user):
    # ensure category provided for budget is valid
    with pytest.raises(ValueError):
        budget = create_budget(test_session, user_id=test_user.id, category="INVALID", monthly_budget=1200.0)

def test_category_validation_transaction(test_session, test_user):
    # ensure category provided for transaction is valid
    with pytest.raises(ValueError):
        transaction = create_transaction(test_session, user_id=test_user.id, amount=100.0, category="INVALID", date=date(2025,1,1))