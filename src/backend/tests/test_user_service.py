import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.infrastructure.db.base import Base
from app.infrastructure.db.models.user_model import UserModel
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
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
def user_service(user_repo):
    return UserService(user_repo)

# -------------------------------
# 2) Tests
# -------------------------------

def test_register_user_creates_user(user_service, test_db):
    email = "test@example.com"
    password = "password123"
    username = "tester"

    user = user_service.register_user(email=email, password=password, username=username)

    assert user.id is not None
    assert user.email == email
    assert user.username == username
    assert verify_password(password, user.password_hash)

def test_register_duplicate_email_raises(user_service):
    email = "dup@example.com"
    password = "password123"
    username1 = "user1"
    username2 = "user2"

    # First registration succeeds
    user_service.register_user(email=email, password=password, username=username1)

    # Second registration with same email fails
    with pytest.raises(ValueError) as excinfo:
        user_service.register_user(email=email, password=password, username=username2)

    assert "already exists" in str(excinfo.value)

def test_login_user_success(user_service):
    email = "login@example.com"
    password = "mypassword"
    username = "loginuser"

    # First, create user
    user_service.register_user(email=email, password=password, username=username)

    # Login
    user = user_service.login_user(email=email, password=password)

    assert user.email == email
    assert user.username == username
    assert user.last_login is not None

def test_login_user_invalid_password_raises(user_service):
    email = "fail@example.com"
    password = "correctpass"
    username = "failuser"

    user_service.register_user(email=email, password=password, username=username)

    with pytest.raises(ValueError) as excinfo:
        user_service.login_user(email=email, password="wrongpass")

    assert "Invalid email or password" in str(excinfo.value)

def test_login_user_nonexistent_email_raises(user_service):
    with pytest.raises(ValueError) as excinfo:
        user_service.login_user(email="noone@example.com", password="pass123")
    assert "Invalid email or password" in str(excinfo.value)

def test_update_user_success(user_service):
    email = "update@example.com"
    password = "password123"
    username = "updateuser"

    # Create user
    user = user_service.register_user(email=email, password=password, username=username)

    # Update fields
    updated_user = user_service.update_user(user.id, {
        "email": "updated@example.com",
        "username": "updateduser"
    })

    assert updated_user.email == "updated@example.com"
    assert updated_user.username == "updateduser"

def test_update_user_single_field(user_service):
    user = user_service.register_user(
        email="single@example.com",
        password="password123",
        username="singleuser"
    )

    updated_user = user_service.update_user(user.id, {
        "username": "newusername"
    })

    assert updated_user.email == "single@example.com"
    assert updated_user.username == "newusername"

def test_update_user_not_found(user_service):
    with pytest.raises(ValueError) as excinfo:
        user_service.update_user(999, {"username": "doesntmatter"})

    assert "User not found" in str(excinfo.value)

def test_update_user_password(user_service):
    user = user_service.register_user(
        email="passupdate@example.com",
        password="oldpassword",
        username="passuser"
    )

    new_hash = hash_password("newpassword")

    updated_user = user_service.update_user(user.id, {
        "password_hash": new_hash
    })

    assert verify_password("newpassword", updated_user.password_hash)
