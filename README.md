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
pyenv shell 3.11
python -m venv .venv
source .venv/bin/activate
# install poetry with pip in the virtual environment
pip install --upgrade pip poetry

# poetry recognizes and installs dependencies in this existing virtual 
# environment
# use --no-root to skip installing this project as a package, since this is
# not a package, but a stand-alone web app
poetry install --no-root
# verify poetry attached virtual environment
poetry env info | grep Path

# run app with fastapi cli
# under the hood, fastapi cli uses built-in uvicorn to run the app
# run fastapi dev mode for development
poetry run fastapi dev
# reset db during app start up
RESET_DB=1 poetry run fastapi dev
# update or create db during app start up, this is for incremental db migration
# and it does not load initial data
UPDATE_DB=1 poetry run fastapi dev

# run fastapi run for production
poetry run fastapi run
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

This option tells fastapi to trust the headers sent by that proxy telling it
that the application is running behind HTTPS.

Build docker image with [Dockerfile](./Dockerfile), and run locally:

```sh
# use RESET_DB env var to reset db and load initial data
# use --no-cache to force rebuild image every time
docker build --no-cache -t example-todo-fastapi . && \
docker run --rm --name example-todo-fastapi -p 8000:8000 -e RESET_DB=1 example-todo-fastapi
# customize LOG_LEVEL=DEBUG
docker run --rm --name example-todo-fastapi -p 8000:8000 -e RESET_DB=1 -e LOG_LEVEL=DEBUG example-todo-fastapi
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
docker buildx build --platform linux/amd64,linux/arm64 -t ikalidocker/example-todo-fastapi:latest --push .
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

## application boostrap with poetry

Assume pyenv is installed in local development environment.

The `pyenv local` command creates a `.python-version` file in the current directory.
It is primarily for local development environments where pyenv is used to manage Python versions.
In containerized deployments, the Python version is typically specified in the Dockerfile, making the .python-version file unnecessary for the container environment.
However, it is still beneficial to include the .python-version file in source control for consistency in local development setups.

```sh
pyenv local 3.11
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip poetry
poetry init --no-interaction
```

If a stand-alone poetry (like brew installed poetry) is used, the
`poetry install` command automatically creates a virtual environment if
not already exists.
This virtual environment is typically created in a directory within current
user profile (e.g., ~/.cache/pypoetry/virtualenvs/).

For local development, it is better to install poetry with pip in the existing
virtual environment, and poetry will recognize the existing virtual environment
and use it for package management. This allows both pip and poetry to point to
the same virtual environment for package management.

In a containerized deployment, the virtual environment is created by poetry
with default location, which is fine for a container, as long as the python
command is run by poetry to ensure the correct python interpreter is used.

In created `pyproject.toml` file, set non-package mode, in order for poetry to
only manage dependencies.

```toml
[tool.poetry]
package-mode = false
```

Add dependencies:

```sh
poetry add ruff --dev
# add fastapi[standard] extra package for fastapi cli and other tools
poetry add fastapi "fastapi[standard]"
poetry add sqlalchemy python-dotenv psycopg2-binary
poetry add pydantic "pydantic[email]"
poetry add jinja2
# introduce filelock to ensure single-process db migration operations
poetry add filelock
# install starlette session middleware
poetry add starsessions
# install multipart support for form and file post
poetry add python-multipart
# install passlib for password hashing
# choose bcrypt as password hashing algorithm
# ref: https://en.wikipedia.org/wiki/Bcrypt
poetry add "passlib[bcrypt]"
# install cryptography lib python-jose for jwt
# JOSE stands for JavaScript Object Signing and Encryption
poetry add "python-jose[cryptography]"
```

## appendix: application boostrap with (pip + requirements.txt)

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
# install starlette session middleware
pip install starsessions
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
