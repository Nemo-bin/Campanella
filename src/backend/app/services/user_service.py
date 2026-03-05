from sqlalchemy.sql import func
from app.repositories.user_repository import UserRepository
from app.utils.security import verify_password

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def login_user(self, email: str, password: str):
        user = self.user_repo.get_user_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise ValueError("Invalid email or password")

        user.last_login = func.now()
        self.user_repo.db.commit()
        self.user_repo.db.refresh(user)

        return user