import os

from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from sqlalchemy import Boolean, Column, Integer, String
from starlette import status

from application.auth.oauth_schemas import oauth2_scheme
from application.auth.oauth_users import Oauth2
from application.database.database import Base, db_dependency
from application.schemas.user import User
from resources import strings


class Users(Base):
    __tablename__ = "app_user"
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(128))
    second_name = Column(String(128))
    username = Column(String(255), index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    disabled = Column(Boolean)

    def __str__(self):
        return f"id= {self.id} - name= {self.username}"

    def __repr__(self):
        return f"<{str(self)}>"

    @classmethod
    def get_user(cls, db, username: str) -> object:
        return db.query(Users).filter(Users.username == username).first()

    def update_password(self, new_password: str):
        self.hashed_password = Oauth2.generate_password(plane_password=new_password)

    @classmethod
    def save_new_user(cls, db, user_create):
        try:
            hashed_password = Oauth2.generate_password(plane_password=user_create)
            db_user = Users(
                first_name=user_create.first_name,
                second_name=user_create.second_name,
                username=user_create.username,
                email=user_create.email,
                hashed_password=hashed_password,
                disabled=user_create.disabled,
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        except Exception as ex:
            raise ex

    @classmethod
    def change_disabled_user(cls, db, username: str) -> object:
        if user := db.query(Users).filter(Users.username == username).first():
            try:
                user.disabled = not user.disabled
                db.commit()
            except Exception as e:
                raise e
            return user

    @staticmethod
    def get_user_current(
        db: db_dependency = db_dependency, token: str = Depends(oauth2_scheme)
    ):
        try:
            token_decode = jwt.decode(
                token=token,
                key=os.getenv("SECRET_KEY"),
                algorithms=[os.getenv("ALGORYTHM")],
            )
            username = token_decode.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=strings.USER_DOES_NOT_EXIST_ERROR,
                )
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=strings.INVALID_CREDENTIALS,
            ) from e
        if user := Users.get_user(username=username, db=db):
            return user
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=strings.USER_DOES_NOT_EXIST_ERROR,
            )

    @staticmethod
    def get_user_disabled_current(user: User = Depends(get_user_current)):
        if user.disabled:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=strings.USER_DISABLED_ERROR,
            )
        return user

    @classmethod
    def authenticate_user(cls, db, username: str, password: str):
        user = Users.get_user(username=username, db=db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=strings.USER_DOES_NOT_EXIST_ERROR,
            )
        if not Oauth2.verify_password(
            plain_password=password, hashed_password=user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=strings.INCORRECT_LOGIN_INPUT,
            )
        return user
