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


# @router.get("/", response_model=list[schemas.TodoReadNested])
@router.get("/", response_model=list[schemas.UserRead])
async def read_users(offset: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = crud.get_users(db, offset=offset, limit=limit)
    return users


# @router.get("/{id}", response_model=schemas.TodoRead)
@router.get("/{id}", response_model=schemas.UserReadNested)
async def read_user(id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user
