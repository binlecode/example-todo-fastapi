from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .models import User

from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    print(f">>>> authenticate user: {user}")
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

ACCESS_TOKEN_EXPIRE_MINUTES = 15
# to generate a secret key for 32char length use:
# openssl rand -hex 32
SECRET_KEY = "2f17fc26a3e6b97883e310a2d43ad730d6545a605d1269be370ec52a5e100b9c"
ALGORITHM = "HS256"

from passlib.context import CryptContext
from jose import JWTError, jwt


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
