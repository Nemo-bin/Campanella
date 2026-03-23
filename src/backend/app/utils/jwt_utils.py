import jwt
import datetime
import uuid


class JWTManager:
    _secret = None
    _refresh_secret = None

    @classmethod
    def init(cls, secret_key: str, refresh_secret_key: str = None):
        cls._secret = secret_key
        cls._refresh_secret = refresh_secret_key

    @classmethod
    def create_access_token(cls, user_id: int, expires_hours: int = 2):
        if cls._secret is None:
            raise RuntimeError("JWT secret not configured")

        data = {
            "user_id": user_id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=expires_hours),
            "iat": datetime.datetime.utcnow(),
        }

        return jwt.encode(data, cls._secret, algorithm="HS256")

    @classmethod
    def create_refresh_token(cls, user_id: int, expires_days: int = 7):
        if cls._refresh_secret is None:
            raise RuntimeError("Refresh JWT secret not configured")

        data = {
            "user_id": user_id,
            "jti": str(uuid.uuid4()),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=expires_days),
            "iat": datetime.datetime.utcnow(),
        }

        return jwt.encode(data, cls._refresh_secret, algorithm="HS256")

    @classmethod
    def decode_access_token(cls, token: str):
        if cls._secret is None:
            raise RuntimeError("JWT secret not configured")

        return jwt.decode(token, cls._secret, algorithms=["HS256"])

    @classmethod
    def decode_refresh_token(cls, token: str):
        if cls._refresh_secret is None:
            raise RuntimeError("Refresh JWT secret not configured")

        return jwt.decode(token, cls._refresh_secret, algorithms=["HS256"])