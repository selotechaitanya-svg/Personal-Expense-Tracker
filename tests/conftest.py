"""Shared pytest fixtures.

The database URL is redirected to a temporary file *before* the application
is imported, so running the tests never touches the real `expenses.db`.
"""

import os
import shutil
import tempfile
from pathlib import Path

import pytest

# Point the app at a throwaway SQLite file in the system temp folder.
_TEMP_DIR = Path(tempfile.mkdtemp(prefix="expense_tracker_tests_"))
os.environ["DATABASE_URL"] = "sqlite:///" + (_TEMP_DIR / "test_expenses.db").as_posix()


@pytest.fixture(scope="session", autouse=True)
def _remove_temp_database():
    """Delete the temporary test database when the whole test run is finished."""
    yield
    shutil.rmtree(_TEMP_DIR, ignore_errors=True)


@pytest.fixture()
def client():
    """A TestClient with a fresh, empty database for every test."""
    from fastapi.testclient import TestClient

    from app.database import Base, engine
    from app.main import app

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with TestClient(app) as test_client:
        yield test_client
