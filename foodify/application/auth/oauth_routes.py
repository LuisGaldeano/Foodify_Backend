from fastapi import APIRouter, Depends
from application.auth.oauth_users import Oauth2
from application.auth.oauth_schemas import oauth2_scheme
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta

from application.models import Users

router = APIRouter()


@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = Users.authenticate_user(username=form_data.username, password=form_data.password)
    access_token_expires = timedelta(minutes=30)
    access_token_jwt = Oauth2.create_token({"sub": user.username}, access_token_expires)
    return {
        "access_token": access_token_jwt,
        "token_type": "bearer"
    }