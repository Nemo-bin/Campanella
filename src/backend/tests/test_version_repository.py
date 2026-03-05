import sys
import flask
import pytest
from unittest.mock import Mock
from sqlalchemy import text

# Import the functions
from app.repositories.version_repository import (
    get_python_version,
    get_flask_version,
    get_postgresql_version,
)

# -------------------------------
# 1) Tests for environment versions
# -------------------------------

def test_get_python_version():
    version = get_python_version()
    assert isinstance(version, str)
    # Should match the major.minor.patch of sys.version
    assert version == sys.version.split()[0]

def test_get_flask_version():
    version = get_flask_version()
    assert isinstance(version, str)
    # Should match flask.__version__
    assert version == flask.__version__

# -------------------------------
# 2) Test PostgreSQL version with mocked DB
# -------------------------------

@pytest.fixture
def mock_db():
    # Mock SQLAlchemy session
    db = Mock()
    # Mock execute().scalar() chain
    db.execute.return_value.scalar.return_value = "PostgreSQL 15.3"
    return db

def test_get_postgresql_version_returns_string(mock_db):
    version = get_postgresql_version(mock_db)
    assert isinstance(version, str)
    assert version == "PostgreSQL 15.3"
    # Ensure execute called with correct SQL
    db_call_arg = mock_db.execute.call_args[0][0]  # first positional argument
    assert str(db_call_arg) == str(text("SELECT version();"))