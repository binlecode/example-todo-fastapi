# Example Todo App with Fastapi and Sqlalchemy

This is a simple todo crud app

-   REST API endpoints for todo crud operations
-   Use pydantic model to validate request body and response data
-   Use Fastapi built-in OAuth 2 password flow for user authentication
-   user authentication is applied to both token validation for API call
    and web session management for web page access
-   jinja2 template + flowbite with tailwindcss for web html
-   web pages use jquery ajax calls to access REST API endpoints for data
-   web pages provide web forms for user login and session based authentication
-   web user session management with starsession middleware
    -   Ref: https://github.com/alex-oleshkevich/starsessions
-   Sqlalchemy db session is injected into route functions via Fastapi Depends()
    function
-   Use Gunicorn as process manager to run Uvicorn workers in a container
-   docker container and docker compose with postgresql db

## run local app

```sh
pyenv shell 3.10
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# run app with uvicorn
# by default, only *.py files are watched for changes, include *.html files too
uvicorn app.main:app --reload --reload-include "*.html"
# with a more verbose format
uvicorn --reload --host $HOST --port $PORT --log-level $LOG_LEVEL "$APP_MODULE"

# reset db during app start up
RESET_DB=1 uvicorn app.main:app --reload
# update or create db during app start up, this is for incremental db migration
# and it does not load initial data
UPDATE_DB=1 uvicorn app.main:app  --reload
```

## SwaggerUI with Openapi doc

Openapi doc for REST endpoints is auto-generated at `http://<host>:<port>/docs`.

## Web pages url

Web pages are built with Jinja2 templates, the home url is `http://<host>:<port>/home`.

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
resource is limited as as dev docker engine.

For production deployment, we should consider multi-process service
in a container.
It is best practice to use Gunicorn to manage Uvicorn worker-class processes
in production deployment:

-   Gunicorn serves as a process manager, it can recycle dead processes
    and restart new processes
-   Uvicorn works as a Gunicorn compatible worker class, so that uvicorn
    worker processes are managed by Gunicorn

Ref: https://fastapi.tiangolo.com/deployment/server-workers/#gunicorn-with-uvicorn-workers

With multiple cpu cores available, the start CMD can be:

```sh
# use UPDATE_DB=1 to update db schema instead of reset and load initial data
LOG_LEVEL=DEBUG RESET_DB=1 gunicorn app.main:app --workers 2 --worker-class \
  uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --log-level debug --reload
```

A [start.sh](./start.sh) script is created to run gunicorn in a container.
In that script, a [gunicorn_conf.py](./gunicorn_conf.py) file is used to
set configurations adaptive to the container resource.

Build docker image with [Dockerfile](./Dockerfile), and run locally:

```sh
docker build -t example-todo-fastapi:test . && \
docker run --rm --name example-todo-fastapi -p 8000:8000 example-todo-fastapi:test
docker run --rm --name example-todo-fastapi -p 8000:8000 -e RESET_DB=1 example-todo-fastapi:test
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

# shutdown and remove containers, but keep images and volumes
docker compose down

# shut down and remove everything including images and volumes
docker compose down --rmi all --volumes
```

## other development notes

To format code, use black and isort.
Isort usually will break black formatting, so run isort first, then run black.

```sh
isort . && black .
```

## appendix: application boostrap

Application dependencies:

```sh
pyenv shell 3.11
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
# install isort form import auto sorting
pip install isort
# install black for code formatting
pip install black
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
# for view templates
pip install jinja2

# save dependencies to requirements.txt
pip freeze > requirements.txt
```

## References

### fastapi docker github

https://github.com/tiangolo/uvicorn-gunicorn-docker
