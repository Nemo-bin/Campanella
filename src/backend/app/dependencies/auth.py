import jwt
from fastapi import HTTPException, Request
from app.utils.jwt_utils import JWTManager


async def get_current_user_id(request: Request) -> int:
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")

    token = auth_header.split(" ")[1]

    try:
        payload = JWTManager.decode_access_token(token)

        user_id = payload.get("user_id")

        if not user_id:
            raise HTTPException(status_code=401, detail="Token missing user_id")

        return user_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")

    except (jwt.InvalidAlgorithmError, jwt.DecodeError):
        raise HTTPException(status_code=401, detail="Invalid token")