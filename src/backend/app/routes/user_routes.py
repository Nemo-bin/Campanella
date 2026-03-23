from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.services.user_service import UserService

from app.dependencies.services import get_user_service
from app.dependencies.auth import get_current_user_id


router = APIRouter(prefix="/users", tags=["users"])


class UpdateUserRequest(BaseModel):
    fields: dict


@router.post("/update")
def update_user(
    data: UpdateUserRequest,
    current_user_id: int = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service)
):

    try:
        user = user_service.update_user(current_user_id, data.fields)
        return user.to_dict()

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/delete")
def delete_user(
    current_user_id: int = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service)
):

    try:
        user_service.delete_user(current_user_id)
        return {"message": "User deleted successfully"}

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))