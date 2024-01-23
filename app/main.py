import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from config import Config

from . import get_logger
from . import schemas
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


@app.get("/home", status_code=200)
def home(request: Request):
    # for TemplateResponse, the context hash must include request object
    return TEMPLATES.TemplateResponse("index.html", {"request": request})


@app.get("/")
def read_root():
    return {"msg": "Todo App with FastAPI"}


@app.get("/health", response_model=schemas.HealthInfo)
def read_health():
    return {"name": "Todo App with FastAPI", "version": app.version}


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(todos.router)


# register database initialization functions in startup event handler
# this is only for local development
# this is NOT for production environment where multiple containers are to
# be deployed
# @app.on_event("startup")
# def on_startup_event():
#     if os.environ.get("RESET_DB"):
#         reset_tables()
