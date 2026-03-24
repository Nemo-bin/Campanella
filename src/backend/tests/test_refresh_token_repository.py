import pytest
from unittest.mock import Mock
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

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(token)

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

    refresh_token_repo.revoke_refresh_token("missing_jti")

    mock_db.get.assert_called_once_with(RefreshTokenModel, "missing_jti")
    mock_db.delete.assert_not_called()
    mock_db.commit.assert_not_called()

# -------------------------------
# 5) Test revoke_all_for_user
# -------------------------------
def test_revoke_all_for_user_with_tokens(refresh_token_repo, mock_db):
    user_id = 7

    token1 = RefreshTokenModel(jti="t1", user_id=user_id)
    token2 = RefreshTokenModel(jti="t2", user_id=user_id)

    query_mock = Mock()
    filter_mock = Mock()

    mock_db.query.return_value = query_mock
    query_mock.filter_by.return_value = filter_mock
    filter_mock.all.return_value = [token1, token2]

    refresh_token_repo.revoke_all_for_user(user_id)

    mock_db.query.assert_called_once_with(RefreshTokenModel)
    query_mock.filter_by.assert_called_once_with(user_id=user_id)
    filter_mock.all.assert_called_once()

    mock_db.delete.assert_any_call(token1)
    mock_db.delete.assert_any_call(token2)
    assert mock_db.delete.call_count == 2

    mock_db.commit.assert_called_once()


def test_revoke_all_for_user_with_no_tokens(refresh_token_repo, mock_db):
    user_id = 7

    query_mock = Mock()
    filter_mock = Mock()

    mock_db.query.return_value = query_mock
    query_mock.filter_by.return_value = filter_mock
    filter_mock.all.return_value = []

    refresh_token_repo.revoke_all_for_user(user_id)

    mock_db.delete.assert_not_called()
    mock_db.commit.assert_called_once()