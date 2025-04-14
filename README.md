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

Latest fastapi supports run cli directly, and is recommended over uvicorn cli.
Under the hood, fastapi cli uses built-in uvicorn to run the app.

```sh
pyenv shell 3.11
python -m venv .venv
source .venv/bin/activate
pip install uv
uv pip install -r requirements.txt

# run fastapi dev mode for development
uv run fastapi dev

# reset db during app start up
RESET_DB=1 uv run fastapi dev

# create or update db during app start up, for incremental db changes
# it does not load initial data
UPDATE_DB=1 uv run fastapi dev

# Legacy: Run uv with uvicorn cli with auto-reload for development
uv run uvicorn app.main:app --reload --log-level debug

# or, Set log level with env var
LOG_LEVEL=DEBUG uv run uvicorn app.main:app --reload
```

## Running in production

For production deployment, the uv command is:

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info
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

Ref: https://fastapi.tiangolo.com/deployment/docker/#create-the-fastapi-code

If container is behind a TLS Termination Proxy (load balancer) like Nginx
or Traefik, add the option `--proxy-headers` to the CMD.
This option tells fastapi to trust the headers sent by that proxy telling it
that the application is running behind HTTPS.

Build docker image with [Dockerfile](./Dockerfile), and run locally:

```sh
# use RESET_DB env var to reset db and load initial data
# use --no-cache to force rebuild image every time
# use LOG_LEVEL=DEBUG
docker build --no-cache -t example-todo-fastapi . && \
docker run --rm --name example-todo-fastapi -p 8000:8000 \
    -e RESET_DB=1 -e LOG_LEVEL=DEBUG example-todo-fastapi
```

Test container endpoints:

```sh
curl -X 'GET' 'http://127.0.0.1:8000/health' -H 'accept: application/json'
# fetch openapi doc and pretty print
curl -X 'GET' 'http://127.0.0.1:8000/openapi.json' -H 'accept: application/json' | jq
```

Or use browser to hit url: `http://127.0.0.1:8000/home` for web page access.

## build multi-platform images and push to dockerhub image registry

In MacOS, run docker buildx to build multi-platform images for x86 amd64 and
arm64. The docker images in docker hub can be deployed to a remote server
such as a kubetnetes cluster.

Use `latest` version tag for the image to push to dockerhub.

```sh
# check docker buildx builder instances
docker buildx ls
# if there's only one builder instance, need to create another builder
# instance to support parallel multi-platform builds
docker buildx create --name mybuilder
# use the builder instance
docker buildx use mybuilder

# dockerhub login with access token in shell env var
# docker login --username=ikalidocker --password=$DOCKERHUB_TOKEN
# recommended, more secure to use stdin pipe to pass token
echo $DOCKERHUB_TOKEN | docker login --username=ikalidocker --password-stdin

# if there are multiple builders active, run multi-platform builds and push in one cli
docker buildx build --platform linux/amd64,linux/arm64 \
    -t ikalidocker/example-todo-fastapi:latest \
    --push .
```

Building image and pushing to dockerhub registry within one docker command has
the advantage that docker will automatically add platform metadata to the
built image. This is useful for kubernetes deployment, where the kubernetes
cluster will automatically pull the correct image for the platform it runs on.

To test run a container from dockerhub image:

```sh
docker pull ikalidocker/example-todo-fastapi:latest && \
docker run --rm --name example-todo-fastapi -p 8000:8000 -e RESET_DB=1 \
    ikalidocker/example-todo-fastapi:latest

# check app is running
curl http://localhost:8000/health
```

## docker-compose

```sh
docker compose up --build

# shutdown and remove containers, but keep images and volumes
docker compose down

# shut down and remove everything including images and volumes
docker compose down --rmi all --volumes
```

## code format and linting

Use ruff for code formatting and linting.

```sh
ruff check --fix
```

## application boostrap

Pyenv is used to set python version.

```sh
pyenv local 3.11
python -m venv .venv
source .venv/bin/activate
pip install uv

# Add dependencies:

uv pip install ruff
# add fastapi[standard] extra package for fastapi cli and other tools
uv pip install fastapi "fastapi[standard]"
uv pip install sqlalchemy python-dotenv psycopg2-binary
uv pip install pydantic "pydantic[email]"
uv pip install jinja2
# introduce filelock to ensure single-process db migration operations
uv pip install filelock
# install starlette session middleware
uv pip install starsessions
# install multipart support for form and file post
uv pip install python-multipart
# install passlib for password hashing
# choose bcrypt as password hashing algorithm
# ref: https://en.wikipedia.org/wiki/Bcrypt
uv pip install "passlib[bcrypt]"
# install cryptography lib python-jose for jwt
# JOSE stands for JavaScript Object Signing and Encryption
uv pip install "python-jose[cryptography]"
```

Create or update requirements.txt.

```bash
uv pip freeze > requirements.txt
```
