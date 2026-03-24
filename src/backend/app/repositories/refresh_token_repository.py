from app.infrastructure.db.models.refresh_token_model import RefreshTokenModel

class RefreshTokenRepository:
        def __init__(self, db):
            self.db = db

        def create_refresh_token(self, jti: str, user_id: int) -> RefreshTokenModel | None:
            token = RefreshTokenModel(
                 jti=jti,
                 user_id=user_id
            )
            self.db.add(token)
            self.db.commit()
            self.db.refresh(token)
            return token
        
        def get_refresh_token(self, jti: str) -> RefreshTokenModel | None:
            return self.db.get(RefreshTokenModel, jti)
        
        def revoke_refresh_token(self, jti: str) -> None:
            token = self.db.get(RefreshTokenModel, jti)
            if token:
                self.db.delete(token)
                self.db.commit()

        def revoke_all_for_user(self, user_id: int) -> None:
            tokens = self.db.query(RefreshTokenModel).filter_by(user_id=user_id).all()
            for token in tokens:
                self.db.delete(token)
            self.db.commit()
