from fastapi import APIRouter, Depends

from application.database.database import db_dependency
from application.models.users import Users
from application.schemas.user import User, UserCreate

router = APIRouter()


@router.get("/users/me")
async def user(user_data: User = Depends(Users.get_user_disabled_current)):
    return user_data


@router.post("/new_user")
async def new_user(db: db_dependency, user_create: UserCreate):
    new_user_created = Users.save_new_user(user_create=user_create, db=db)
    return new_user_created


@router.post("/change_disabled")
async def change_disabled(
    db: db_dependency, user_change: User = Depends(Users.get_user_disabled_current)
):
    user_updated = Users.change_disabled_user(username=user_change.username, db=db)
    return user_updated
