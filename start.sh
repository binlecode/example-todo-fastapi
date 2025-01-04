#! /usr/bin/env sh
set -e

# if RESET_DB is not set, check UPDATE_DB, if not set, default to UPDATE_DB=1
if [ -z "$RESET_DB" ]; then
    export UPDATE_DB=${UPDATE_DB:-1}
fi
echo "RESET_DB: $RESET_DB"
echo "UPDATE_DB: $UPDATE_DB"

# add gunicorn_conf.py file to gunicorn config
export GUNICORN_CONF=${GUNICORN_CONF:-"./gunicorn_conf.py"}
# set default worker class
export WORKER_CLASS=${WORKER_CLASS:-"uvicorn.workers.UvicornWorker"}

# run this command with pip + requirements.txt package management
# exec gunicorn app.main:app -k "$WORKER_CLASS" -c "$GUNICORN_CONF"

# run this command with poetry + pyproject.toml package management
exec poetry run gunicorn app.main:app -k "$WORKER_CLASS" -c "$GUNICORN_CONF"