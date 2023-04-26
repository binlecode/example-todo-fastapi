import os
from dotenv import load_dotenv
import logging


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env.sample"))


class Config(object):
    # LOG_LEVEL = logging.INFO
    LOG_LEVEL = logging.DEBUG

    # Config.SQLALCHEMY_DATABASE_URI = "sqlite:///./sqlite.db"
    # Config.SQLALCHEMY_DATABASE_URI = "postgresql://user:password@postgresserver/db"
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "SQLALCHEMY_DATABASE_URI", ""
    ) or "sqlite:///" + os.path.join(basedir, "sqlite.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    OAUTH2_TOKEN_URL = "/api/auth/token"

    PAGINATION_LIMIT = 5
