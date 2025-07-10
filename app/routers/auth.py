from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from jose import JWTError
from sqlalchemy.orm import Session

from config import Config
from app import schemas
from app import crud
from app.db import get_db
from app.models import User
from app.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    decode_access_token,
)

router = APIRouter(prefix="/auth", dependencies=[], tags=["Auth"])


@router.post("/token", response_model=schemas.Token)
def login_for_token(
    form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


# define a token-to-user interceptor as a dependency function
# this is to be used for all route functions that requires token-user check
# throws 401 if check not successful
#
# by OAuth2 spec, any HTTP error status 401 returns a `WWW-Authenticate` header
# in our case (Bearer token), the value should be set to "Bearer"
#
def get_current_user_by_token(
    token: str = Depends(schemas.oauth2_password_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user


@router.get("/me", response_model=schemas.UserRead)
def read_logged_in_user(
    current_user: User = Depends(get_current_user_by_token),
):
    return current_user
