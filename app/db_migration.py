import logging
from .db import engine
from .models import Base
from .db import SessionLocal
from .models import User, Todo
from config import Config


logging.basicConfig(level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)


def init_tables():
    logger.info(">> sqlalchemy dropping existing tables")
    Base.metadata.drop_all(engine)
    logger.info(">> sqlalchemy creating tables")
    Base.metadata.create_all(engine)


def migrate_data():
    # load users
    db = SessionLocal()

    u1 = User(
        lname="Doe",
        fname="John",
        email="johndoe@example.com",
        # plain pswd: "secret"
        hashed_password="$2b$12$mV7rTpEAAk77POssNFkBfO.F0UvhU5Z2llYTbu3RcS8s8C3S2hNUC",
    )
    u2 = User(
        fname="Alice",
        lname="Wonderson",
        email="alice@example.com",
        # plain pswd: "secret2"
        hashed_password="$2b$12$Th16FzsG7bexKod7DpgKZORxIpoV1E8hu0Xh/jZOhM2hAJV03HKCu",
    )
    db.add_all([u1, u2])
    db.commit()

    db.add_all(
        [
            Todo(
                text="Bake french bread",
                owner=u1,
            ),
            Todo(
                text="Water flower",
                owner=u1,
            ),
            Todo(
                text="Play outdoor tennis",
                owner=u2,
            ),
        ]
    )
    db.commit()
