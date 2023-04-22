
```sh
# use sqlalchemy for data models
pip install sqlalchemy
pip install fastapi 
pip install pydantic "pydantic[email]"
pip install uvicorn
# install passlib for password hashing
# choose bcrypt as password hashing algorithm
# ref: https://en.wikipedia.org/wiki/Bcrypt
pip install "passlib[bcrypt]"
```



```sh
uvicorn app.main:app --reload
# reset local sqlite db during app start up
RESET_DB=true uvicorn app.main:app --reload
```


## pydantic

To convert Sqlalchemy orm model data into pydantic validation schema, 
the schema (pydantic model) has to load custom config with `orm_mode = True`.

