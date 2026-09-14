"""
database.py

SQLite database setup using SQLAlchemy. We use SQLite because this is a
final-year prototype: zero setup, single file, good enough for a demo.

Two responsibilities live here:
1. The SQLAlchemy engine/session (shared across the app).
2. `init_db()` which creates tables on first run.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./support.db"

# check_same_thread=False is required because FastAPI can use a different
# thread per request while SQLite defaults to single-thread access.
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db():
    """Create all tables if they do not already exist. Called on startup."""
    import models  # noqa: F401 (import here to register models with Base)
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
