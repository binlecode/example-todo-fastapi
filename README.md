# Example Todo App with Fastapi and Sqlalchemy

This is a simple todo crud REST api app with sqlalchemy ORM.

- Sqlalchemy db session is injected into route functions via Fastapi Depends()
  function
- Fastapi has built-in OAuth 2 password flow user authentication support, it is
  used in this app for token based access control
- Use pydantic model to validate request body and response data
- Use Gunicorn as process manager to run Uvicorn workers in a container

## run local app

```sh
pyenv shell 3.10
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# run app with uvicorn
uvicorn app.main:app --reload
# with a more verbose format
uvicorn --reload --host $HOST --port $PORT --log-level $LOG_LEVEL "$APP_MODULE"

# reset db during app start up
RESET_DB=1 uvicorn app.main:app --reload
# update or create db during app start up, this is for incremental db migration
# and it does not load initial data
UPDATE_DB=1 uvicorn app.main:app --reload
```

## SwaggerUI with Openapi doc

Openapi doc is auto-generated at `http://<host>:<port>/docs`.

## pydantic

To convert Sqlalchemy orm model data into pydantic validation schema,
the schema (pydantic model) has to load custom config with
`from_attributes = True`.

## build and run container

If container is behind a TLS Termination Proxy (load balancer) like Nginx
or Traefik, add the option `--proxy-headers` to the CMD.

This option tells Uvicorn to trust the headers sent by that proxy telling it
that the application is running behind HTTPS.

See [unicorn-start-reload](./start-uvicorn.sh) shell script for details.

This should be fine for simple use cases where the load is light and container
resource allocation is moderate (low resource values of virtual cpu, aka
equal or less than 1 vcpu).

For performance intensive use cases, such as highly concurrent requests and
processing intensive services, we should consider multi-process service
in a container.

Uvicorn could run with `--workers` option to enable multiple workers,
but it does not provide any process monitoring or management, thus it is not
suitable for production.

It is common practice to use Gunicorn to manage Uvicorn worker-class processes:

- Gunicorn can be used as a process manager, it can recycle dead processes
  and restart new processes
- Uvicorn can work as a Gunicorn compatible worker class, so that a uvicorn
  worker process can be managed by Gunicorn

Ref: https://fastapi.tiangolo.com/deployment/server-workers/#gunicorn-with-uvicorn-workers

In deployment environemnt where multiple cpu cores are available for a container,
the start CMD can be:

```sh
# set workers number to a static number, which should be equal or less than cpu core number
LOG_LEVEL=DEBUG UPDATE_DB=1 gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:80 --log-level debug --reload
```

A gunicorn_conf.py file is used to hold adaptive settings for linux OS base image.

See [start.sh](./start.sh) script for details.

Build docker image with [Dockerfile](./Dockerfile), and run locally:

```sh
docker build -t example-todo-fastapi:test . && \
docker run --rm --name example-todo-fastapi -p 80:80 example-todo-fastapi:test
```

test container endpoints:

```sh
curl -X 'GET' 'http://127.0.0.1/health' -H 'accept: application/json'
# fetch openapi doc and pretty print
curl -X 'GET' 'http://127.0.0.1/openapi.json' -H 'accept: application/json' | jq
```

or use browser to hit url: http://127.0.0.1/docs


## docker-compose

```sh
docker compose up --build
```



## application setup

Application dependencies:

```sh
pyenv shell 3.10
python -m venv venv
source venv/bin/activate
pip install --upgrade pip isort black
# use sqlalchemy for data models
pip install sqlalchemy
pip install fastapi
pip install python-dotenv
# install multipart support for form and file post
pip install python-multipart
pip install pydantic "pydantic[email]"
pip install uvicorn
# install gunicorn + unicorn standard extra package for deployment
pip install "uvicorn[standard]" gunicorn
# install passlib for password hashing
# choose bcrypt as password hashing algorithm
# ref: https://en.wikipedia.org/wiki/Bcrypt
pip install "passlib[bcrypt]"
# install cryptography lib python-jose for jwt
# JOSE stands for JavaScript Object Signing and Encryption
pip install "python-jose[cryptography]"
# introduce filelock to ensure single-process db migration operations
pip install filelock
# for postgresql db
pip install psycopg2-binary

# save dependencies to requirements.txt
pip freeze > requirements.txt
```

## References

### fastapi docker github

https://github.com/tiangolo/uvicorn-gunicorn-docker
