import pytest
from unittest.mock import Mock, call
import uuid

from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.infrastructure.db.models.refresh_token_model import RefreshTokenModel

# -------------------------------
# 1) Fixture for mock DB
# -------------------------------
@pytest.fixture
def mock_db():
    db = Mock()
    return db

@pytest.fixture
def refresh_token_repo(mock_db):
    return RefreshTokenRepository(mock_db)

# -------------------------------
# 2) Test create_refresh_token
# -------------------------------
def test_create_refresh_token_calls_db_methods(refresh_token_repo, mock_db):
    jti = str(uuid.uuid4())
    user_id = 42

    token = refresh_token_repo.create_refresh_token(jti=jti, user_id=user_id)

    # Should add token
    mock_db.add.assert_called_once()
    # Should commit
    mock_db.commit.assert_called_once()
    # Should refresh
    mock_db.refresh.assert_called_once_with(token)

    # Returned object should have correct attributes
    assert token.jti == jti
    assert token.user_id == user_id

# -------------------------------
# 3) Test get_refresh_token
# -------------------------------
def test_get_refresh_token_returns_token(refresh_token_repo, mock_db):
    fake_token = RefreshTokenModel(jti="abc123", user_id=1)
    mock_db.get.return_value = fake_token

    result = refresh_token_repo.get_refresh_token("abc123")

    mock_db.get.assert_called_once_with(RefreshTokenModel, "abc123")
    assert result == fake_token

def test_get_refresh_token_returns_none_if_missing(refresh_token_repo, mock_db):
    mock_db.get.return_value = None

    result = refresh_token_repo.get_refresh_token("missing_jti")

    mock_db.get.assert_called_once_with(RefreshTokenModel, "missing_jti")
    assert result is None

# -------------------------------
# 4) Test revoke_refresh_token
# -------------------------------
def test_revoke_refresh_token_existing_token(refresh_token_repo, mock_db):
    fake_token = RefreshTokenModel(jti="abc123", user_id=1)
    mock_db.get.return_value = fake_token

    refresh_token_repo.revoke_refresh_token("abc123")

    mock_db.get.assert_called_once_with(RefreshTokenModel, "abc123")
    mock_db.delete.assert_called_once_with(fake_token)
    mock_db.commit.assert_called_once()

def test_revoke_refresh_token_missing_token(refresh_token_repo, mock_db):
    mock_db.get.return_value = None

    # Should not raise error
    refresh_token_repo.revoke_refresh_token("missing_jti")

    mock_db.get.assert_called_once_with(RefreshTokenModel, "missing_jti")
    mock_db.delete.assert_not_called()
    mock_db.commit.assert_not_called()