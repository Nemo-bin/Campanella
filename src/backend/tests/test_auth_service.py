import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.infrastructure.db.base import Base
from app.infrastructure.db.models.user_model import UserModel
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.utils.security import hash_password, verify_password

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
def auth_service(user_repo):
    return AuthService(user_repo)

# -------------------------------
# 2) Tests
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
