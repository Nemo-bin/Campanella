from sqlalchemy.orm import Session
from fastapi import Depends

from app.repositories.user_repository import UserRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository

from .db import get_db

def get_user_repository(db: Session = Depends(get_db)):
    return UserRepository(db)

def get_refresh_token_repository(db: Session = Depends(get_db)):
    return RefreshTokenRepository(db)