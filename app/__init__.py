import logging
from logging import Logger
import os
from config import Config


# config logger based on deployment environment
def get_logger(logger_name=None) -> Logger:
    logger_name = logger_name or __name__
    logger = logging.getLogger(logger_name)
    print(f"logger_name: {logger_name}")

    print(f"SERVER_SOFTWARE: {os.environ.get('SERVER_SOFTWARE', '')}")
    # configure logging
    # check if fastapi app is served by gunicorn
    if "gunicorn" in os.environ.get("SERVER_SOFTWARE", ""):
        logger.info("fastapi app is served by gunicorn")
        # overwrite the default logger to use gunicorn logger
        # Get the Gunicorn logger
        gunicorn_logger = logging.getLogger("gunicorn.error")
        # Overwrite the default logger to use Gunicorn logger
        logger.handlers = gunicorn_logger.handlers
        logger.setLevel(gunicorn_logger.level)
        logger.info(
            f"logger {logger.name} is overwritten to use gunicorn logger: {gunicorn_logger}"
        )
        logger.info(f"fastapi app logger level: {logging.getLevelName(logger.level)}")
    else:
        logger.setLevel(Config.LOG_LEVEL)
        logger.info("fastapi app is served by fastapi buit-in server")
        logger.info(f"fastapi app logger level: {logging.getLevelName(logger.level)}")

    return logger
