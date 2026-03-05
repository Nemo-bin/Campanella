from sqlalchemy.exc import IntegrityError
from app.infrastructure.db.models.user_model import UserModel
from app.utils.security import verify_password

class UserRepository:
    def __init__(self, db):
        self.db = db

    def create_user(self, email: str, password_hash: str, username: str) -> UserModel:
        user = UserModel(
            email=email,
            password_hash=password_hash,
            username=username,
            
        )

        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise ValueError("User with this email or username already exists")
    
    def get_user_by_email(self, email):
        return self.db.query(UserModel).filter(UserModel.email == email).first()