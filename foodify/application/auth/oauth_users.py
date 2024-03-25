import os
from datetime import datetime, timedelta
from typing import Union

from jose import jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Oauth2:
    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def generate_password(plane_password):
        if type(plane_password) is not str:
            return pwd_context.hash(plane_password.password)
        return pwd_context.hash(plane_password)

    @classmethod
    def create_token(cls, data: dict, time_expire: Union[timedelta, None] = None):
        data_copy = data.copy()
        if time_expire is None:
            expires = datetime.utcnow() + timedelta(minutes=15)
        else:
            expires = datetime.utcnow() + time_expire

        data_copy["exp"] = expires
        return jwt.encode(
            data_copy,
            key=os.getenv("SECRET_KEY", "test_key"),
            algorithm=os.getenv("ALGORYTHM", "HS256"),
        )
