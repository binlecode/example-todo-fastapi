# Example Todo App with Fastapi and Sqlalchemy

This is a simple todo crud REST api app with sqlalchemy ORM.

Sqlalchemy db session is injected into route functions via Fastapi Depends()
function.

Fastapi has built-in OAuth 2 password flow user authentication support, it is
used in this app for token based access control.

## environment setup

```sh
# use sqlalchemy for data models
pip install sqlalchemy
pip install fastapi
# install multipart support for form and file post
pip install python-multipart 
pip install pydantic "pydantic[email]"
pip install uvicorn
# install passlib for password hashing
# choose bcrypt as password hashing algorithm
# ref: https://en.wikipedia.org/wiki/Bcrypt
pip install "passlib[bcrypt]"
# install cryptography lib python-jose for jwt
# JOSE stands for JavaScript Object Signing and Encryption
pip install "python-jose[cryptography]"
```

## run local app

```sh
uvicorn app.main:app --reload
# reset local sqlite db during app start up
RESET_DB=true uvicorn app.main:app --reload
```

## pydantic

To convert Sqlalchemy orm model data into pydantic validation schema,
the schema (pydantic model) has to load custom config with `orm_mode = True`.

