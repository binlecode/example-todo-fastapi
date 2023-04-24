# express the schema of incoming/outgoing data using pydantic models
# and use these models as type hint for auto validation and conversion
# these models (better called 'schemas`) are data shape specs.

from datetime import datetime
from pydantic import BaseModel
from pydantic import EmailStr
from fastapi.security.oauth2 import OAuth2PasswordBearer

## OAuth 2 access token
OAUTH2_TOKEN_URL = "/api/auth/token"
oauth2_password_scheme = OAuth2PasswordBearer(tokenUrl=OAUTH2_TOKEN_URL)


class HealthInfo(BaseModel):
    name: str
    version: str


class Token(BaseModel):
    access_token: str
    token_type: str


## User schemas


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    lname: str
    fname: str
    password: str


class UserRead(UserBase):
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


## Todo schemas


class TodoCreate(BaseModel):
    text: str
    completed: bool = False


class TodoUpdate(TodoCreate):
    id: int


class TodoRead(TodoUpdate):
    owner_id: str
    # owner: UserRead
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# nested view model includes child orm objects


# be careful to only use UserRead, not UserReadNested
# otherwise it will lead to endless circular lazy loading...
class TodoReadNested(TodoRead):
    owner: UserRead


class UserReadNested(UserRead):
    todos: list[TodoRead]
