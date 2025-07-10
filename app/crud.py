from sqlalchemy.orm import Session

from config import Config

from app import schemas
from app.models import Todo, User
from app.security import get_password_hash

PAGINATION_LIMIT = Config.PAGINATION_LIMIT


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, offset: int = 0, limit: int = PAGINATION_LIMIT):
    return db.query(User).offset(offset).limit(limit).all()


def create_user(db: Session, user_data: schemas.UserCreate) -> User:
    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        is_superuser=user_data.is_superuser,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# todo: split into separate crud python files for each model


def create_todo(db: Session, owner_user: User, todo_data: schemas.TodoCreate):
    todo = Todo(
        text=todo_data.text,
        completed=todo_data.completed,
        owner=owner_user,
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


def update_todo(db: Session, id: int, todo_data: schemas.TodoUpdate):
    todo = db.query(Todo).filter(Todo.id == id).first()
    todo.text = todo_data.text
    todo.completed = todo_data.completed
    db.commit()
    db.refresh(todo)
    return todo


def delete_todo(db: Session, id: int):
    todo = db.query(Todo).filter(Todo.id == id).first()
    db.delete(todo)
    db.commit()


def get_todo(db: Session, id: int):
    return db.query(Todo).get(id)


def get_todos(db: Session, offset: int = 0, limit: int = PAGINATION_LIMIT):
    return db.query(Todo).offset(offset).limit(limit).all()


def get_user_todos(
    db: Session, user_id: int, offset: int = 0, limit: int = PAGINATION_LIMIT
):
    return (
        db.query(Todo)
        .filter(Todo.owner_id == user_id)
        .offset(offset)
        .limit(limit)
        .all()
    )
