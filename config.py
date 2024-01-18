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

    OAUTH2_TOKEN_URL = "/api/auth/token"

    PAGINATION_LIMIT = 5
