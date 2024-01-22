#! /usr/bin/env sh
set -e

# general gunicorn config is in /code/gunicorn_conf.py
export GUNICORN_CONF=${GUNICORN_CONF:-"/code/gunicorn_conf.py"}
export WORKER_CLASS=${WORKER_CLASS:-"uvicorn.workers.UvicornWorker"}
exec gunicorn app.main:app -k "$WORKER_CLASS" -c "$GUNICORN_CONF"