import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

from app.infrastructure.db.base import Base
from app.infrastructure.db.models.user_model import UserModel
from app.infrastructure.db.models.refresh_token_model import RefreshTokenModel
from app.repositories.user_repository import UserRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.services.auth_service import AuthService
from app.utils.security_utils import hash_password, verify_password
import uuid

# -------------------------------
# 1) Test DB setup (in-memory SQLite)
# -------------------------------

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:", echo=False)
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def user_repo(test_db):
    return UserRepository(test_db)

@pytest.fixture
def refresh_token_repo(test_db):
    return RefreshTokenRepository(test_db)

@pytest.fixture
def auth_service(user_repo, refresh_token_repo):
    return AuthService(user_repo, refresh_token_repo)

# -------------------------------
# 2) User tests
# -------------------------------

def test_register_user_creates_user(auth_service, test_db):
    email = "test@example.com"
    password = "password123"
    username = "tester"

    user = auth_service.register_user(email=email, password=password, username=username)

    assert user.id is not None
    assert user.email == email
    assert user.username == username
    assert verify_password(password, user.password_hash)

def test_register_duplicate_email_raises(auth_service):
    email = "dup@example.com"
    password = "password123"
    username1 = "user1"
    username2 = "user2"

    # First registration succeeds
    auth_service.register_user(email=email, password=password, username=username1)

    # Second registration with same email fails
    with pytest.raises(ValueError) as excinfo:
        auth_service.register_user(email=email, password=password, username=username2)

    assert "already exists" in str(excinfo.value)

def test_login_user_success(auth_service):
    email = "login@example.com"
    password = "mypassword"
    username = "loginuser"

    # First, create user
    auth_service.register_user(email=email, password=password, username=username)

    # Login
    user = auth_service.login_user(email=email, password=password)

    assert user.email == email
    assert user.username == username
    assert user.last_login is not None

def test_login_user_invalid_password_raises(auth_service):
    email = "fail@example.com"
    password = "correctpass"
    username = "failuser"

    auth_service.register_user(email=email, password=password, username=username)

    with pytest.raises(ValueError) as excinfo:
        auth_service.login_user(email=email, password="wrongpass")

    assert "Invalid email or password" in str(excinfo.value)

def test_login_user_nonexistent_email_raises(auth_service):
    with pytest.raises(ValueError) as excinfo:
        auth_service.login_user(email="noone@example.com", password="pass123")
    assert "Invalid email or password" in str(excinfo.value)

# -------------------------------
# 3) Refresh token / is_valid tests
# -------------------------------

def test_is_valid_returns_true_for_existing_token(auth_service, refresh_token_repo):
    # Generate a fake refresh token jti
    jti = str(uuid.uuid4())
    refresh_token_repo.create_refresh_token(jti=jti, user_id=1)

    assert auth_service.is_valid(jti) is True

def test_is_valid_returns_false_for_nonexistent_token(auth_service):
    fake_jti = str(uuid.uuid4())
    assert auth_service.is_valid(fake_jti) is False

# -------------------------------
# 4) Refresh token save / revoke tests
# -------------------------------

def test_save_refresh_token_persists_token(auth_service, refresh_token_repo):
    user_id = 1
    jti = str(uuid.uuid4())

    auth_service.save_refresh_token(jti=jti, user_id=user_id)

    token = refresh_token_repo.get_refresh_token(jti)

    assert token is not None
    assert token.jti == jti
    assert token.user_id == user_id


def test_revoke_refresh_token_deletes_token(auth_service, refresh_token_repo):
    user_id = 1
    jti = str(uuid.uuid4())

    # Save token first
    refresh_token_repo.create_refresh_token(jti=jti, user_id=user_id)

    # Ensure it exists
    assert refresh_token_repo.get_refresh_token(jti) is not None

    # Revoke it
    auth_service.revoke_refresh_token(jti)

    # Should now be gone
    assert refresh_token_repo.get_refresh_token(jti) is None