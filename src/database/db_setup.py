from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def setup_database():
    # setup db engine
    engine = create_engine("sqlite:///transactions.db")

def get_session(engine):
    session = sessionmaker(bind=engine)
    return session()

if __name__ == "__main__":
    engine = setup_database()
    session = get_session(engine)
    session.close()