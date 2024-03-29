from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Config

SQLALCHEMY_DATABASE_URI = Config.SQLALCHEMY_DATABASE_URI

# set check_same_thread to false specifically for sqlite3 file database
# This is to allow multiple threads to access same connection in FastAPI
# Ref: https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#pysqlite-threading-pooling
# check_same_thread custom setting is not needed for other databases
if SQLALCHEMY_DATABASE_URI.startswith("sqlite:"):
    connect_args = {"check_same_thread": False}
else:
    connect_args = {}

engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
    connect_args=connect_args,
    # enable sql statements logging for debug/development
    echo=True,
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# create the FastAPI's dependency function for db session

# def get_db():
#     """provide db session to path operation functions"""
#     try:
#         db = SessionLocal()
#         yield db
#     finally:
#         db.close()


# prefer context-manager (with .. as ..) syntax, which auto-closes session
def get_db():
    with SessionLocal() as db:
        yield db
