import pytest
from unittest.mock import Mock
from app.services.version_service import get_stack_versions

# -------------------------------
# 1) Fixtures
# -------------------------------

@pytest.fixture
def mock_db():
    # Mock DB session for PostgreSQL version
    db = Mock()
    # Mock execute().scalar() chain for get_postgresql_version
    db.execute.return_value.scalar.return_value = "PostgreSQL 15.3"
    return db

# -------------------------------
# 2) Tests
# -------------------------------

def test_get_stack_versions_returns_versions(mock_db):
    versions = get_stack_versions(mock_db)

    # Check keys exist
    assert "python" in versions
    assert "flask" in versions
    assert "postgresql" in versions

    # Check PostgreSQL version comes from mocked DB
    assert versions["postgresql"] == "PostgreSQL 15.3"

    # Python and Flask versions should be non-empty strings
    assert isinstance(versions["python"], str)
    assert isinstance(versions["flask"], str)
    assert len(versions["python"]) > 0
    assert len(versions["flask"]) > 0

def test_postgresql_version_called(mock_db):
    # Call stack versions
    get_stack_versions(mock_db)

    # Ensure execute() was called on the db
    mock_db.execute.assert_called_once()