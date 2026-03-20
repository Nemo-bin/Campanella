import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.infrastructure.db.base import Base
from app.infrastructure.db.models.user_model import UserModel
from app.repositories.user_repository import UserRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.utils.security_utils import hash_password, verify_password

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
def user_service(user_repo):
    return UserService(user_repo)

@pytest.fixture
def auth_service(user_repo, refresh_token_repo):
    return AuthService(user_repo, refresh_token_repo)

# -------------------------------
# 2) Tests
# -------------------------------

def test_update_user_single_field(auth_service, user_service):
    user = auth_service.register_user(
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

def test_update_user_password(auth_service, user_service):
    user = auth_service.register_user(
        email="passupdate@example.com",
        password="oldpassword",
        username="passuser"
    )

    new_hash = hash_password("newpassword")

    updated_user = user_service.update_user(user.id, {
        "password_hash": new_hash
    })

    assert verify_password("newpassword", updated_user.password_hash)
