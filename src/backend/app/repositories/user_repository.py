from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from app.infrastructure.db.models.user_model import UserModel

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
        
    def get_user_by_id(self, id: int) -> UserModel | None:
        return self.db.get(UserModel, id)
    
    def get_user_by_email(self, email: str) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.email == email)
        return self.db.execute(stmt).scalar_one_or_none()
    
    def get_user_by_username(self, username: str) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.username == username)
        return self.db.execute(stmt).scalar_one_or_none()

    def update(self, id: int, fields: dict) -> UserModel | None:
        user = self.db.get(UserModel, id)

        if user is None:
            raise ValueError("User not found")
        
        for key, value in fields.items():
            setattr(user, key, value)

        return user

    def delete(self, id: int) -> None:
        user = self.db.get(UserModel, id)

        if user is None:
            raise ValueError("User not found")
        
        self.db.delete(user)
        self.db.commit()