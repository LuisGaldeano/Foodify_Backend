from pydantic import BaseModel, EmailStr, Field, constr


class UserBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=128)
    second_name: str = Field(min_length=1, max_length=128)
    username: constr(to_lower=True, strip_whitespace=True)
    email: EmailStr
    disabled: bool | None = None


class UserCreate(UserBase):
    password: str


class User(UserBase):
    pass


class UserInDB(User):
    hashed_password: str
