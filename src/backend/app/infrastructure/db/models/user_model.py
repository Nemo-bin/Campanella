from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.infrastructure.db.base import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    username = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    profile_picture = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)