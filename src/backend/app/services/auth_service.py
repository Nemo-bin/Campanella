from sqlalchemy.sql import func
from app.repositories.user_repository import UserRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.utils.security import verify_password, hash_password

class AuthService:
    def __init__(self, user_repo: UserRepository, refresh_token_repo: RefreshTokenRepository):
        self.user_repo = user_repo
        self.refresh_token_repo = refresh_token_repo

    def register_user(self, email: str, password: str, username: str):
        password_hash = hash_password(password)
        return self.user_repo.create_user(email=email, password_hash=password_hash, username=username)

    def login_user(self, email: str, password: str):
        user = self.user_repo.get_user_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password")

        user.last_login = func.now()
        self.user_repo.db.commit()
        self.user_repo.db.refresh(user)

        return user
    
    def is_valid(self, jti: str) -> bool:
        return self.refresh_token_repo.get_refresh_token(jti) is not None