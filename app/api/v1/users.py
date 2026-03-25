from fastapi import APIRouter, Depends

from app.models.user import UserCreate
from app.services.user_service import UserService

users_router = APIRouter()


def get_user_service() -> UserService:
    return UserService()


@users_router.post("/")
def create_user(
    user: UserCreate, user_service: UserService = Depends(get_user_service)
):
    user_service.create_user(
        user.first_name, user.last_name, user.email, user.password, user.phone
    )
    return {"status": "success", "code": 201}
