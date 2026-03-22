from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.middleware.auth_middleware import AuthMiddleware
from app.infrastructure.db import get_db


router = APIRouter(prefix="/users", tags=["users"])


class UpdateUserRequest(BaseModel):
    fields: dict


@router.post("/update")
def update_user(
    data: UpdateUserRequest,
    current_user_id: int = Depends(AuthMiddleware.required),
    db: Session = Depends(get_db)
):
    repo = UserRepository(db)
    service = UserService(repo)

    try:
        user = service.update_user(current_user_id, data.fields)
        return user.to_dict()

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/delete")
def delete_user(
    current_user_id: int = Depends(AuthMiddleware.required),
    db: Session = Depends(get_db)
):
    repo = UserRepository(db)
    service = UserService(repo)

    try:
        service.delete_user(current_user_id)
        return {"message": "User deleted successfully"}

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))