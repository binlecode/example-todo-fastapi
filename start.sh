#! /usr/bin/env sh
set -e

if [ -f /code/gunicorn_conf.py ]; then
    echo "Loading gunicorn configuration from gunicorn_conf.py file"
    DEFAULT_GUNICORN_CONF=/code/gunicorn_conf.py
fi
export GUNICORN_CONF=${GUNICORN_CONF:-$DEFAULT_GUNICORN_CONF}
export WORKER_CLASS=${WORKER_CLASS:-"uvicorn.workers.UvicornWorker"}

# If there's a prestart.sh script, run it before starting
PRE_START_PATH=${PRE_START_PATH:-/code/prestart.sh}
echo "Checking for script in $PRE_START_PATH"
if [ -f $PRE_START_PATH ] ; then
    echo "Running script $PRE_START_PATH"
    . "$PRE_START_PATH"
else 
    echo "There is no script $PRE_START_PATH"
fi

# Start Gunicorn
exec gunicorn app.main:app -k "$WORKER_CLASS" -c "$GUNICORN_CONF"