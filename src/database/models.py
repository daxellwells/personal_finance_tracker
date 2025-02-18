from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship, declarative_base, validates
from datetime import date

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True,nullable=False)
    password = Column(String, nullable=False)

    transactions = relationship("Transaction", back_populates="user", cascade="all, delete")
    budgets = relationship("Budget", back_populates='user', cascade="all, delete")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    description = Column(String, nullable=True)

    user = relationship("User", back_populates="transactions")

    # ✅ Enforce constraint using @validates
    @validates('amount')
    def validate_amount(self, key, value):
        if value == 0:
            raise ValueError("Transaction amount cannot be zero.")
        return value

    @validates('date')
    def validate_date(self, key, value):
        if not isinstance(value, date):
            raise ValueError("Invalid date format. Must be a `date` object.")
        return value

class Budget(Base):
    __tablename__ = 'budgets'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String, nullable=False)
    monthly_budget = Column(Float, nullable=False)

    user = relationship("User", back_populates="budgets")

    #enforces positive budget
    @validates('monthly_budget')
    def validate_budget(self, key, value):
        if value < 0:
            raise ValueError("Budget amount must be positive")
        return value