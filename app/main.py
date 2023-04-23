import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import users, todos
from .db_migration import init_tables, migrate_data


app = FastAPI(
    dependencies=[],
    title="Todo App with FastAPI OpenAPI doc",
    version="0.0.1",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # "*",
        "http://127.0.0.1:8000",  # allow local (/docs) swagger-ui
    ],
    # allow cookies for cross-origin requests, when allow_credentials is set
    # True, allow_origins can not be set to ["*"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"hello": "fastapi!"}


@app.get("/async")
async def read_root_async():
    return {"hello": "fastapi async!"}


app.include_router(users.router)
app.include_router(todos.router)


# register startup event handler
@app.on_event("startup")
async def on_startup_event():
    # perform database initialization and data load
    if os.environ.get("RESET_DB"):
        print(">> initializing tables")
        init_tables()
        print(">> loading initial data")
        migrate_data()
