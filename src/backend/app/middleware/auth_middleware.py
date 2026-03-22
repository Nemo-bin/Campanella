import jwt
import datetime
import uuid

from fastapi import HTTPException, Request


class AuthMiddleware:
    _secret = None
    _refresh_secret = None

    @classmethod
    def init(cls, secret_key: str, refresh_secret_key: str = None):
        cls._secret = secret_key
        cls._refresh_secret = refresh_secret_key

    @classmethod
    async def required(cls, request: Request) -> int:
        if cls._secret is None:
            raise HTTPException(status_code=500, detail="JWT secret not configured")

        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing token")

        token = auth_header.split(" ")[1]

        try:
            data = jwt.decode(token, cls._secret, algorithms=["HS256"])

            current_user_id = data.get("user_id")

            if not current_user_id:
                raise HTTPException(status_code=401, detail="Token missing user_id")

            return current_user_id

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")

        except (jwt.InvalidAlgorithmError, jwt.DecodeError):
            raise HTTPException(status_code=401, detail="Invalid token")

    @classmethod
    def create_jwt(cls, user_id: int, expires_hours: int = 2):
        data = {
            "user_id": user_id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=expires_hours),
            "iat": datetime.datetime.utcnow(),
        }

        return jwt.encode(data, cls._secret, algorithm="HS256")

    @classmethod
    def create_refresh_token(cls, user_id: int, expires_days: int = 7):
        data = {
            "user_id": user_id,
            "jti": str(uuid.uuid4()),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=expires_days),
            "iat": datetime.datetime.utcnow(),
        }

        return jwt.encode(data, cls._refresh_secret, algorithm="HS256")