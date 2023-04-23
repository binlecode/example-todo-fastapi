from fastapi import APIRouter, Depends
from fastapi import HTTPException, status

from sqlalchemy.orm import Session

from app.db import get_db
from .. import schemas
from .. import crud

router = APIRouter(prefix="/api/users", dependencies=[])


@router.post("/signup", response_model=schemas.UserRead)
async def signup(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, user_data.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered."
        )
    signed_up_user = crud.create_user(db, user_data)
    return signed_up_user
