from datetime import timedelta

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from application.auth.oauth_users import Oauth2
from application.database.database import db_dependency
from application.models import Users

router = APIRouter()


@router.post("/token")
def login(db: db_dependency, form_data: OAuth2PasswordRequestForm = Depends()):
    user = Users.authenticate_user(
        username=form_data.username, password=form_data.password, db=db
    )
    access_token_expires = timedelta(minutes=30)
    access_token_jwt = Oauth2.create_token({"sub": user.username}, access_token_expires)
    return {"access_token": access_token_jwt, "token_type": "bearer"}
