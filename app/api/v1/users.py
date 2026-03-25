from fastapi import APIRouter, Depends, HTTPException, status

from app.models.user import UserCreate, UserRead
from app.services.user_service import UserService

users_router = APIRouter()


def get_user_service() -> UserService:
    return UserService()


@users_router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserRead)
def create_user(
    user: UserCreate, user_service: UserService = Depends(get_user_service)
):
    new_user = user_service.create_user(
        user.first_name, user.last_name, user.email, user.password, user.phone
    )
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )
    return new_user
