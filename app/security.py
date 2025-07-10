import logging
from datetime import datetime, timedelta

from passlib.context import CryptContext
from sqlalchemy.orm import Session
from jose import jwt


from config import Config

from app.models import User

logging.basicConfig(level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    logger.info(f">> authenticate user: {user}")
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


# jwt token encryption and decryption
# use HSA symmetric encryption for simplicity, one secret_key is used
# for both encryption and decryption.
# to use RSA asymmetric encryption, a pair of private, public keys are used
# usually public key should be distributed by a jwks endpoint by OAuth 2 specs

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = Config.ACCESS_TOKEN_EXPIRE_MINUTES
# to generate a secret key for 32char length use:
# openssl rand -hex 32
SECRET_KEY = Config.SECRET_KEY


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if not expires_delta:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# if token has audience claim, then decode MUST supply audience argument
# https://pyjwt.readthedocs.io/en/stable/usage.html?highlight=audience#audience-claim-aud
def decode_access_token(token: str, audience: str = None, options: dict = {}):
    """
    Params:
        options: dict
            varify_aud: enable or disable aud (audience) verification
    Raises:
        all Exceptions from jwt.decode() method
    """
    payload = jwt.decode(
        token, SECRET_KEY, algorithms=[ALGORITHM], audience=audience, options=options
    )
    # payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], audience=audience, options={"varify_aud": False})
    return payload
