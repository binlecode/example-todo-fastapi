# Example Todo App with Fastapi and Sqlalchemy

This is a simple todo crud REST api app with sqlalchemy ORM.

Sqlalchemy db session is injected into route functions via Fastapi Depends()
function.

Fastapi has built-in OAuth 2 password flow user authentication support, it is
used in this app for token based access control.

## environment setup

Install by requirements.txt:

```sh
pip install -r requirements.txt
```

Or, install manually for newer lib versions for development / upgrade:

```sh
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
```

## run local app

```sh
uvicorn app.main:app --reload
# with a more verbose format
uvicorn --reload --host $HOST --port $PORT --log-level $LOG_LEVEL "$APP_MODULE"

# reset local sqlite db during app start up
RESET_DB=true uvicorn app.main:app --reload
```

## Openapi doc

Openapi doc is auto-generated at `http://<host>:<port>/docs`.


## pydantic

To convert Sqlalchemy orm model data into pydantic validation schema,
the schema (pydantic model) has to load custom config with `orm_mode = True`.

## deployment and container scripts

When develop locally, uvicorn runs in a single process.

For a container image, the start CMD can run uvicorn in single process:

```sh
exec uvicorn --reload --host $HOST --port $PORT --log-level $LOG_LEVEL "$APP_MODULE"
```

Note, if container is behind a TLS Termination Proxy (load balancer) like Nginx
or Traefik, add the option `--proxy-headers` to the CMD.

This option tells Uvicorn to trust the headers sent by that proxy telling it
that the application is running behind HTTPS.

```sh
CMD ["uvicorn", "app.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]
```

See [unicorn-start-reload](./uvicorn-start-reload.sh) shell script for details.

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
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:80

# or, use gunicorn_conf.py that holds adaptive settings for linux OS container env
gunicorn app.main:app -c gunicorn_conf.py --worker-class uvicorn.workers.UvicornWorker
```

See [start.sh](./start.sh) script for details.

Note that Fastapi's on_event("startup") handler will run for each worker
during app startup.

## build image and run container

build docker image with [Dockerfile](./Dockerfile)

```sh
docker build -t example-todo-fastapi .
```

In this Dockerfile, a local sqlite.db file is copied over to bypass external
database dependency.

run container locally:

```sh
docker run -d --name example-todo-fastapi -p 80:80 example-todo-fastapi
```

test container endpoints:

```sh
curl -X 'GET' 'http://127.0.0.1/health' -H 'accept: application/json'
# fetch openapi doc and pretty print
curl -X 'GET' 'http://127.0.0.1/openapi.json' -H 'accept: application/json' | jq
```

or use browser to hit url: http://127.0.0.1/docs

## References

### fastapi docker github

https://github.com/tiangolo/uvicorn-gunicorn-docker
