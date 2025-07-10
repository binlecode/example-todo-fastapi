from functools import wraps
from filelock import FileLock, Timeout
from app import get_logger
from app.db import SessionLocal, engine
from app.models import Base, Todo, User

# logging.basicConfig(level=Config.LOG_LEVEL)
# logger = logging.getLogger(__name__)
logger = get_logger(__name__)


# decorator to lock a function with a file lock:
# - ensure only one process can run it at a time
# - quit locking trial once timeout is reached
# This is ONLY useful for multiple worker processes deployment with one
# virtual machine, if there are distributed multiple virtual machines,
# the file lock will not work as it only prevents multiple processes by
# a file in the same virtual machine.
def with_lock(lockfile, timeout=0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            lock = FileLock(lockfile)
            try:
                lock.acquire(timeout=timeout)
                logger.debug(f"locked {lockfile}")
                return func(*args, **kwargs)
            except Timeout:
                logger.error(f"failed to acquire lock {lockfile}")
                return
            finally:
                lock.release()
                logger.debug(f"released {lockfile}")

        return wrapper

    return decorator


# todo: need a distributed lock solution for multiple virtual machines deployment
#   such as redis lock, database lock, etc.
#   Note that for database lock the underlying table should NOT be part of
#   salalchemy models, otherwise it will cause deadlock in shema migrations.


@with_lock("reset_table.lock")
def reset_tables():
    logger.info(">> sqlalchemy dropping existing tables")
    Base.metadata.drop_all(engine)
    logger.info(">> sqlalchemy creating or updating tables")
    Base.metadata.create_all(engine)
    logger.info(">> sqlalchemy loading initial data")
    init_data()


@with_lock("update_table.lock")
def update_tables():
    logger.info(">> sqlalchemy creating or updating tables")
    Base.metadata.create_all(engine)


def init_data():
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
                completed=True,
            ),
            Todo(
                text="Play outdoor tennis",
                owner=u2,
            ),
            Todo(
                text="Buy groceries",
                owner=u2,
            ),
            Todo(
                text="Learn a new programming language",
                owner=u1,
            ),
            Todo(
                text="Read a book about artificial intelligence",
                owner=u1,
                completed=True,
            ),
            Todo(
                text="Start a personal coding project",
                owner=u2,
            ),
            Todo(
                text="Take a course on data science",
                owner=u2,
                completed=True,
            ),
            Todo(
                text="Write a blog post about a recent tech discovery",
                owner=u1,
            ),
            Todo(
                text="Contribute to an open source project",
                owner=u2,
            ),
            Todo(
                text="Explore a new technology or framework",
                owner=u1,
            ),
            Todo(
                text="Create a portfolio website",
                owner=u2,
            ),
            Todo(
                text="Attend a tech meetup or conference",
                owner=u1,
            ),
            Todo(
                text="Build a mobile app",
                owner=u2,
            ),
        ]
    )
    db.commit()
