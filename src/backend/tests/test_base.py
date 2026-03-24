import pytest
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
import datetime

from app.infrastructure.db.base import Base

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

# -------------------------------
# 2) Test model
# -------------------------------

class TestModel(Base):
    __tablename__ = "test_model"

    id = Column(Integer, primary_key=True)
    email = Column(String)
    password_hash = Column(String)
    created_at = Column(DateTime)
    last_login = Column(DateTime, nullable=True)

# -------------------------------
# 3) Fixtures
# -------------------------------

@pytest.fixture
def test_instance(test_db):
    instance = TestModel(
        email="test@example.com",
        password_hash="secret_hash",
        created_at=datetime.datetime(2024, 1, 1, 12, 0, 0),
        last_login=None
    )

    test_db.add(instance)
    test_db.commit()
    test_db.refresh(instance)

    return instance

# -------------------------------
# 4) to_dict tests
# -------------------------------

def test_to_dict_returns_basic_fields(test_instance):
    result = test_instance.to_dict()

    assert result["id"] == test_instance.id
    assert result["email"] == "test@example.com"

def test_to_dict_hides_password_hash(test_instance):
    result = test_instance.to_dict()

    assert "password_hash" not in result

def test_to_dict_converts_datetime_to_iso(test_instance):
    result = test_instance.to_dict()

    assert isinstance(result["created_at"], str)
    assert result["created_at"] == test_instance.created_at.isoformat()

def test_to_dict_handles_none_datetime(test_instance):
    result = test_instance.to_dict()

    assert result["last_login"] is None