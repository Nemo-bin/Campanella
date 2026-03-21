from sqlalchemy.sql import func
from app.repositories.user_repository import UserRepository

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    def update_user(self, user_id: int, fields: dict):
        user = self.user_repo.update(user_id, fields)
        self.user_repo.db.commit()
        return user
    
    def delete_user(self, user_id: int):
        self.user_repo.delete(user_id)