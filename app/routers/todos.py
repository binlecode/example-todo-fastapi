from fastapi import APIRouter, Depends
from fastapi import HTTPException, status

from sqlalchemy.orm import Session

from app.db import get_db
from .. import schemas
from .. import crud

router = APIRouter(prefix="/api/todos", dependencies=[])


# @router.get("/", response_model=list[schemas.TodoReadNested])
@router.get("/", response_model=list[schemas.TodoRead])
async def read_todos(
    user_id: int = None, offset: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    if user_id:
        todos = crud.get_user_todos(db, user_id)
    else:
        todos = crud.get_todos(db, offset=offset, limit=limit)
    print(">>>> todos: ", todos)
    return todos


# @router.get("/{id}", response_model=schemas.TodoRead)
@router.get("/{id}", response_model=schemas.TodoReadNested)
async def read_todo(id: int, db: Session = Depends(get_db)):
    todo = crud.get_todo(db, id)
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return todo


@router.post("/", response_model=schemas.TodoRead)
async def create_todo(todo_data: schemas.TodoCreate, db: Session = Depends(get_db)):
    todo = crud.create_todo(db, todo_data)
    return todo
