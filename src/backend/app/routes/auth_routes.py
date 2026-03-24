from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import jwt

from app.utils.jwt_utils import JWTManager
from app.dependencies.services import get_auth_service
from app.dependencies.auth import get_current_user_id


router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: str
    username: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str
    user_id: int

class LogoutRequest(BaseModel):
    refresh_token: str


@router.post("/register", status_code=201)
async def register_user(
    data: RegisterRequest, 
    auth_service = Depends(get_auth_service)
    ):

    try:
        user = auth_service.register_user(
            email=data.email,
            password=data.password,
            username=data.username
        )

        access_token = JWTManager.create_access_token(user.id)
        refresh_token = JWTManager.create_refresh_token(user.id)

        jti = JWTManager.decode_refresh_token(refresh_token).get("jti")
        auth_service.save_refresh_token(jti=jti, user_id=user.id)

        return {
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
async def login_user(
    data: LoginRequest, 
    auth_service = Depends(get_auth_service)
    ):

    try:
        user = auth_service.login_user(
            email=data.email,
            password=data.password
        )

        access_token = JWTManager.create_access_token(user.id)
        refresh_token = JWTManager.create_refresh_token(user.id)

        jti = JWTManager.decode_refresh_token(refresh_token).get("jti")
        auth_service.save_refresh_token(jti=jti, user_id=user.id)

        return {
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token
        }

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/refresh")
async def refresh_token(
    data: RefreshRequest, 
    auth_service = Depends(get_auth_service)
    ):

    try:
        jti = JWTManager.decode_refresh_token(data.refresh_token).get("jti")

        if not auth_service.is_valid(jti):
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        new_access_token = JWTManager.create_access_token(data.user_id)
        return {"access_token": new_access_token}

    except jwt.ExpiredSignatureError as e:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except (jwt.InvalidAlgorithmError, jwt.DecodeError):
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.post("/logout")
async def logout_user(
    data: LogoutRequest,
    current_user_id: int = Depends(get_current_user_id),
    auth_service = Depends(get_auth_service)
):
    try:
        jti = JWTManager.decode_refresh_token(data.refresh_token).get("jti")
        token_user_id = JWTManager.decode_refresh_token(data.refresh_token).get("user_id")

        if token_user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Token does not belong to user")

        auth_service.revoke_refresh_token(jti)
        return {"message": "Logged out successfully"}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except (jwt.InvalidAlgorithmError, jwt.DecodeError):
        raise HTTPException(status_code=401, detail="Invalid refresh token")