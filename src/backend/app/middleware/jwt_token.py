import jwt
from functools import wraps
from flask import request
import datetime
import os

class AuthMiddleware:
    _secret = None

    @classmethod
    def init(cls, secret_key: str):
        cls._secret = secret_key

    @classmethod
    def required(cls, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if cls._secret is None:
                raise Exception("No JWT key")

            token = None
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

            if not token:
                raise Exception("Token missng")

            try:
                data = jwt.decode(token, cls._secret, algorithms=["HS256"])
                current_user_id = data.get("user_id")
                if not current_user_id:
                    raise Exception("Token does not contain user_id")

            except jwt.ExpiredSignatureError:
                raise Exception("Token expired")
            except (jwt.InvalidAlgorithmError, jwt.DecodeError):
                raise Exception("Invalid token")

            return f(current_user_id, *args, **kwargs)

        return decorated
    
    @classmethod
    def create_jwt(cls, user_id: int, expires_hours: int = 2):
        data = {
            "user_id": user_id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=expires_hours),
            "iat": datetime.datetime.utcnow()
        }

        token = jwt.encode(data, cls._secret, algorithm="HS256")
        return token