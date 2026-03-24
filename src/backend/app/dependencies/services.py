from fastapi import Depends

from app.repositories.user_repository import UserRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository

from app.services.auth_service import AuthService
from app.services.user_service import UserService

from .repositories import get_refresh_token_repository, get_user_repository

def get_auth_service(
        user_repo: UserRepository = Depends(get_user_repository),
        refresh_token_repo: RefreshTokenRepository = Depends(get_refresh_token_repository)
    ):
    return AuthService(user_repo, refresh_token_repo)

def get_user_service(
        user_repo: UserRepository = Depends(get_user_repository)
    ):
    return UserService(user_repo)