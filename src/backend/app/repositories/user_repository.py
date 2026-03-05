from app.infrastructure.db.models.user_model import UserModel

class UserRepository:
    def __init__(self, db):
        self.db = db

    def create_user(self, email, password_hash):
        user = UserModel(
            email=email,
            password_hash=password_hash
        )

        self.db.add(user)
        self.db.commit()

        return user
    
    def get_user_by_email(self, email):
        return (
            self.db.query(UserModel)
            .filter(UserModel.email == email)
            .first()
        )