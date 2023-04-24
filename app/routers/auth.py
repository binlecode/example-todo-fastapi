from sqlalchemy.orm import Session
from jose import JWTError
from datetime import timedelta

from fastapi import APIRouter, Depends
from fastapi import HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm


from ..db import get_db
from ..security import authenticate_user
from ..security import create_access_token
from ..security import ACCESS_TOKEN_EXPIRE_MINUTES
from ..security import decode_access_token

from ..models import User

from .. import schemas


router = APIRouter(prefix="/api/auth", dependencies=[])


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
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


@router.get("/me", response_model=schemas.UserRead)
def read_logged_in_user(
    current_user: User = Depends(get_current_user_by_token),
    db: Session = Depends(get_db),
):
    return current_user
