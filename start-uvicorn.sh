#! /usr/bin/env sh
set -e

HOST=${HOST:-0.0.0.0}
PORT=${PORT:-80}
LOG_LEVEL=${LOG_LEVEL:-info}

# Start Uvicorn with single process
exec uvicorn app.main:app --reload --host $HOST --port $PORT --log-level $LOG_LEVEL