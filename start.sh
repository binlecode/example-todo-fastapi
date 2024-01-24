#! /usr/bin/env sh
set -e

# if RESET_DB is not set, check UPDATE_DB, if not set, default to UPDATE_DB=1
if [ -z "$RESET_DB" ]; then
    export UPDATE_DB=${UPDATE_DB:-1}
fi
echo "RESET_DB: $RESET_DB"
echo "UPDATE_DB: $UPDATE_DB"

# general gunicorn config is in /code/gunicorn_conf.py
export GUNICORN_CONF=${GUNICORN_CONF:-"/code/gunicorn_conf.py"}
export WORKER_CLASS=${WORKER_CLASS:-"uvicorn.workers.UvicornWorker"}
exec gunicorn app.main:app -k "$WORKER_CLASS" -c "$GUNICORN_CONF"