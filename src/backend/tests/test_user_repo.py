import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from app.infrastructure.db.base import Base
from app.infrastructure.db.models.user_model import UserModel
from app.repositories.user_repository import UserRepository
from app.utils.security import hash_password

# -------------------------------
# 1) Test DB setup
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

# -------------------------------
# 2) Tests
# -------------------------------

def test_create_user(user_repo):
    email = "repo@test.com"
    password_hash = hash_password("mypassword")
    username = "repouser"

    user = user_repo.create_user(email=email, password_hash=password_hash, username=username)

    assert user.id is not None
    assert user.email == email
    assert user.username == username

def test_create_duplicate_user_raises(user_repo):
    email = "dup@test.com"
    password_hash = hash_password("mypassword")
    username1 = "user1"
    username2 = "user2"

    # First user
    user_repo.create_user(email=email, password_hash=password_hash, username=username1)

    # Duplicate email
    with pytest.raises(ValueError) as excinfo:
        user_repo.create_user(email=email, password_hash=password_hash, username=username2)
    assert "already exists" in str(excinfo.value)

def test_get_user_by_email(user_repo):
    email = "find@test.com"
    password_hash = hash_password("pass123")
    username = "finduser"

    user_repo.create_user(email=email, password_hash=password_hash, username=username)

    user = user_repo.get_user_by_email(email)
    assert user is not None
    assert user.email == email
    assert user.username == username

def test_get_user_by_username(user_repo):
    email = "uname@test.com"
    password_hash = hash_password("pass123")
    username = "uniqueuser"

    user_repo.create_user(email=email, password_hash=password_hash, username=username)

    user = user_repo.get_user_by_username(username)
    assert user is not None
    assert user.email == email
    assert user.username == username

def test_get_user_by_id(user_repo):
    email = "id@test.com"
    password_hash = hash_password("pass123")
    username = "iduser"

    user = user_repo.create_user(email=email, password_hash=password_hash, username=username)

    fetched_user = user_repo.get_user_by_id(user.id)
    assert fetched_user is not None
    assert fetched_user.id == user.id
    assert fetched_user.email == email