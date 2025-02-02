import typing
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, Depends, status
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from starsessions import CookieStore, SessionMiddleware
from starsessions import load_session

from config import Config

from . import get_logger
from . import schemas
from . import crud
from .models import User
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

# stores session data in a signed cookie on the client.
# use a strong secret key to sign the cookie for production security
session_store = CookieStore(secret_key=Config.SECRET_KEY)
app.add_middleware(
    SessionMiddleware,
    store=session_store,
    # by default, cookie lifetime is limited to the browser session
    # manually set session lifetime to 14 days
    lifetime=3600 * 24 * 14,
    # by default, cookie is set to be accessible only via https
    # manually set cookie to be accessible via http as well
    cookie_https_only=False,
)


# interceptor for current_user from session-based authentication
# can be depency-injected into template response functions
async def get_current_user_by_session_id(
    request: Request, db: Session = Depends(get_db)
):
    # get user_id from starlette session
    # session is not autoloaded by default for performance reasons
    # load session to request selectively for necessary routes
    await load_session(request)
    user_id = request.session.get("user_id")
    if user_id is None:
        return None
    user = crud.get_user(db, user_id)
    return user


# initialize html templates
BASE_PATH = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))


# view routes should be excluded from swagger docs
@app.get("/home", include_in_schema=False)
async def home(
    request: Request, current_user: User = Depends(get_current_user_by_session_id)
):
    logger.debug(f"current_user: {current_user}")
    if current_user is None:
        redirect_url = request.url_for("login")
        # set status code 302 to ensure redirect results in a GET request
        return RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)

    return TEMPLATES.TemplateResponse(
        "todos.html",
        # for TemplateResponse, the context hash must include request object
        {
            "request": request,
            "current_user": current_user,
            # "flashed_messages": get_flashed_messages(request),
            "flashed_messages": await get_flashed_messages(request),
        },
    )


@app.get("/logout", include_in_schema=False)
async def logout(request: Request):
    # clear user_id from session
    await load_session(request)
    request.session.pop("user_id", None)

    await flash(request, "You have been logged out.", category="warning")

    redirect_url = request.url_for("login")
    # set status code is 302 to ensure redirect results in a GET request
    response = RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)
    return response


@app.get("/login", include_in_schema=False)
async def login(request: Request):
    await load_session(request)
    return TEMPLATES.TemplateResponse(
        "login.html",
        {
            "request": request,
            "flashed_messages": await get_flashed_messages(request),
        },
    )


@app.post("/login", include_in_schema=False)
async def post_login(
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

    # update user id in starlette session
    await load_session(request)
    request.session["user_id"] = user.id

    await flash(request, "You have been logged in.", category="success")

    redirect_url = request.url_for("home")
    logger.debug(f"redirect_url: {redirect_url}")
    # set status code is 302 to ensure redirect results in a GET request
    return RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)


@app.get("/")
def read_root():
    return {"msg": "Todo App with FastAPI"}


@app.get("/health", response_model=schemas.HealthInfo)
def read_health():
    return {"name": "Todo App with FastAPI", "version": app.version}


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(todos.router)


# flash messages helper to push messages to session for one-time display
async def flash(
    request: Request, message: typing.Any, category: str = "success"
) -> None:
    await load_session(request)
    if "_messages" not in request.session:
        request.session["_messages"] = []
    request.session["_messages"].append({"message": message, "category": category})


# pop flashed messages from session for one-time display
async def get_flashed_messages(request: Request):
    await load_session(request)
    return request.session.pop("_messages") if "_messages" in request.session else []
