from fastapi import APIRouter, Depends
from application.auth.oauth_users import Oauth2
from application.database.database import session
from application.models.users import Users
from application.schemas.user import UserCreate, User

router = APIRouter()


@router.get("/users/me")
async def user(user_data: User = Depends(Users.get_user_disabled_current)):
    return user_data


@router.post("/new_user")
async def new_user(user_create: UserCreate):
    new_user_created = Users.save_new_user(user_create=user_create)
    return new_user_created

@router.post("/change_disabled")
async def change_disabled(user: User = Depends(Users.get_user_disabled_current)):
    user_updated = Users.change_disabled_user(username=user.username)
