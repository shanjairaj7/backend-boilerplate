"""
SQLite Database Configuration with SQLAlchemy
Auto-created for all new projects
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import os

# Dynamic SQLite database path - unique per deployment
DATABASE_NAME = os.getenv("DATABASE_NAME", "app_database.db")
DATABASE_URL = f"sqlite:///./{DATABASE_NAME}"

print(f"🗄️ Using database: {DATABASE_NAME}")

# Create engine with SQLite settings
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required for SQLite
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()

@contextmanager
def get_db_session():
    """Database session context manager for manual operations"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db():
    """FastAPI dependency injection for database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables - call this in your service files"""
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """Drop all database tables - useful for testing"""
    Base.metadata.drop_all(bind=engine)