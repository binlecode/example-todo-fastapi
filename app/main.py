import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, users, todos
from .db_migration import init_tables, migrate_data
from . import schemas
from config import Config

logging.basicConfig(level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="Todo App with FastAPI OpenAPI doc",
    version="0.0.1",
    dependencies=[],
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


@app.get("/")
def read_root():
    return {"msg": "Todo App with FastAPI"}


@app.get("/health", response_model=schemas.HealthInfo)
def read_health():
    return {"name": "Todo App with FastAPI", "version": app.version}


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(todos.router)


# register startup event handler
@app.on_event("startup")
def on_startup_event():
    # perform database initialization and data load
    if os.environ.get("RESET_DB"):
        logger.info(">> initializing tables")
        init_tables()
        logger.info(">> loading initial data")
        migrate_data()
