from sqlalchemy import Column, Integer, String, ForeignKey
from app.infrastructure.db.base import Base

class RefreshTokenModel(Base):
    __tablename__ = "refresh_token"

    jti = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)