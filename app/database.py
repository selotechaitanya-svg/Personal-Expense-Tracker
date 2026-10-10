"""Database configuration and session management for the Expense Tracker API.

This module is the only place that knows how the database is connected.
Everything else (models, routes) asks this module for a session.
"""

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

DATABASE_URL = settings.database_url

# SQLite needs this so a request can be handled by a different thread
# than the one that created the connection (FastAPI and TestClient do that).
if DATABASE_URL.startswith("sqlite"):
    CONNECT_ARGS = {"check_same_thread": False}
    # Ensure parent directory exists for SQLite files (e.g. ./data or /app/data)
    if ":///" in DATABASE_URL:
        db_path_part = DATABASE_URL.split(":///", 1)[1]
        if db_path_part and not db_path_part.startswith(":memory:"):
            db_dir = Path(db_path_part).parent
            if db_dir and not db_dir.exists():
                db_dir.mkdir(parents=True, exist_ok=True)
    engine = create_engine(DATABASE_URL, connect_args=CONNECT_ARGS)
else:
    # Production PostgreSQL / MySQL connection pooling settings
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )

# Factory used to create database sessions.
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    """Base class that all SQLAlchemy models inherit from."""


def init_db() -> None:
    """Create all database tables if they do not already exist."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency that yields a database session.

    The session is always closed when the request finishes, even if the
    request raised an error.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

