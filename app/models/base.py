from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

# Create the SQLAlchemy base class
Base = declarative_base()

# Create database directory if it doesn't exist
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db")
os.makedirs(DB_DIR, exist_ok=True)

# Database URL
DATABASE_URL = f"sqlite:///{os.path.join(DB_DIR, 'calls.db')}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# This is kept for backward compatibility but we'll use init_db.py instead
def init_db():
    from app.db.init_db import init_database
    init_database() 