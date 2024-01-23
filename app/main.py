import logging
import os
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, Depends, status
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from config import Config

from . import get_logger
from . import schemas
from . import crud
from .security import authenticate_user
from .db import get_db
from .db_migration import reset_tables, update_tables
from .routers import auth, todos, users

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.environ.get("RESET_DB"):
        reset_tables()
    elif os.environ.get("UPDATE_DB"):
        update_tables()
    # yield to boot up the app
    yield
    # cleanup work after the app has finished
    logger.info("Application has finished.")


app = FastAPI(
    title="Todo App with FastAPI",
    version="0.3",
    dependencies=[],
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
        # "http://127.0.0.1:8000",  # allow local (/docs) swagger-ui
    ],
    # allow cookies for cross-origin requests, when allow_credentials is set
    # True, allow_origins can not be set to ["*"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# initialize html templates
BASE_PATH = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))


@app.get("/home")
def home(request: Request, db: Session = Depends(get_db)):
    # for TemplateResponse, the context hash must include request object
    return TEMPLATES.TemplateResponse(
        "todos.html",
        {
            "request": request,
            "current_user": get_authenticated_user_from_session_id(request, db),
        },
    )


@app.get("/logout")
def logout(request: Request):
    # clear cookie for session_id
    redirect_url = request.url_for("login")
    response = RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="session_id")
    return response


@app.get("/login")
def login(request: Request):
    # for TemplateResponse, the context hash must include request object
    return TEMPLATES.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # handle login form submission
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        return TEMPLATES.TemplateResponse(
            "login.html", {"request": request}, status_code=status.HTTP_401_UNAUTHORIZED
        )

    # when login is successful, redirect to home page
    session_id = create_session(user.id)
    # set cookie for session_id
    redirect_url = request.url_for("home")
    logger.debug(f"redirect_url: {redirect_url}")
    # set status code is 302 to ensure redirect results in a GET request
    response = RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="session_id", value=session_id)
    return response


@app.get("/")
def read_root():
    return {"msg": "Todo App with FastAPI"}


@app.get("/health", response_model=schemas.HealthInfo)
def read_health():
    return {"name": "Todo App with FastAPI", "version": app.version}


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(todos.router)


# todo: move this in-memory session store to an external session store
#   such as redis or pgsql
sessions = {}


# util for web session creation, for web UI user session management
def create_session(user_id: int):
    session_id = str(uuid.uuid4())
    sessions[session_id] = user_id
    return session_id


# Custom middleware for session-based authentication
def get_authenticated_user_from_session_id(request: Request, db: Session):
    session_id = request.cookies.get("session_id")
    if session_id is None:
        return None
    # Get the user from the session
    user_id = sessions.get(session_id)
    if user_id is None:
        return None
    user = crud.get_user(db, user_id)
    return user
