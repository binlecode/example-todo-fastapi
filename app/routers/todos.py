from fastapi import APIRouter, Depends
from fastapi import HTTPException, status

from sqlalchemy.orm import Session

from ..db import get_db
from ..models import User
from .. import schemas
from .. import crud
from .auth import get_current_user_by_token

router = APIRouter(prefix="/api/todos", dependencies=[])


# @router.get("/", response_model=list[schemas.TodoReadNested])
@router.get("/", response_model=list[schemas.TodoRead])
def read_todos(
    user_id: int = None, offset: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    if user_id:
        todos = crud.get_user_todos(db, user_id)
    else:
        todos = crud.get_todos(db, offset=offset, limit=limit)
    return todos


# @router.get("/{id}", response_model=schemas.TodoRead)
@router.get("/{id}", response_model=schemas.TodoReadNested)
def read_todo(id: int, db: Session = Depends(get_db)):
    todo = crud.get_todo(db, id)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
        )
    return todo


# secured by token
@router.post("/", response_model=schemas.TodoRead, status_code=status.HTTP_201_CREATED)
def create_todo(
    todo_data: schemas.TodoCreate,
    current_user: User = Depends(get_current_user_by_token),
    db: Session = Depends(get_db),
):
    owner = current_user
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Owner not found"
        )

    todo = crud.create_todo(db, owner, todo_data)
    return todo


# secured by token
@router.put("/{id}", response_model=schemas.TodoRead, status_code=status.HTTP_200_OK)
def update_todo(
    id: str,
    todo_data: schemas.TodoUpdate,
    current_user: User = Depends(get_current_user_by_token),
    db: Session = Depends(get_db),
):
    todo = crud.update_todo(db, id, todo_data)
    return todo
