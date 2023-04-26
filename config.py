import os
from dotenv import load_dotenv
import logging


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config:
    # LOG_LEVEL = logging.INFO
    LOG_LEVEL = logging.DEBUG

    # SQLALCHEMY_DATABASE_URL = os.environ["SQLALCHEMY_DATABASE_URL"]
    SQLALCHEMY_DATABASE_URL = "sqlite:///./sqlite.db"
    # SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

    OAUTH2_TOKEN_URL = "/api/auth/token"

    PAGINATION_LIMIT = 5
