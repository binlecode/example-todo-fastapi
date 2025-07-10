import logging
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env.sample"))

logger = logging.getLogger(__name__)


class Config(object):
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    logger.setLevel(LOG_LEVEL)
    logger.info(f"LOG_LEVEL: {LOG_LEVEL}")

    # Config.SQLALCHEMY_DATABASE_URI = "sqlite:///./sqlite.db"
    # Config.SQLALCHEMY_DATABASE_URI = "postgresql://user:password@postgresserver/db"
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "SQLALCHEMY_DATABASE_URI", ""
    ) or "sqlite:///" + os.path.join(basedir, "sqlite.db")
    logger.info(f"SQLALCHEMY_DATABASE_URI: {SQLALCHEMY_DATABASE_URI}")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    logger.info(f"SQLALCHEMY_TRACK_MODIFICATIONS: {SQLALCHEMY_TRACK_MODIFICATIONS}")

    # secret key for signing cookies (web) and tokens (api)
    SECRET_KEY = os.getenv("SECRET_KEY") or "TOP SECRET"
    logger.info(f"SECRET_KEY: {SECRET_KEY[:8]}...")

    API_PREFIX = os.environ.get("API_PREFIX", "/api/v1")
    logger.info(f"API_PREFIX: {API_PREFIX}")

    OAUTH2_TOKEN_URL = f"{API_PREFIX}/auth/token"
    logger.info(f"OAUTH2_TOKEN_URL: {OAUTH2_TOKEN_URL}")

    ACCESS_TOKEN_EXPIRE_MINUTES = 15
    logger.info(f"ACCESS_TOKEN_EXPIRE_MINUTES: {ACCESS_TOKEN_EXPIRE_MINUTES}")

    PAGINATION_LIMIT = 5
    logger.info(f"PAGINATION_LIMIT: {PAGINATION_LIMIT}")
