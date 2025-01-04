# Use the official Python image as a base image
FROM python:3.11-slim

# Set environment variables
# Prevents Python from writing .pyc files which are unnecessary in a container.
ENV PYTHONDONTWRITEBYTECODE=1
# Ensures that output is sent straight to the terminal without being buffered, which is useful for logging.
ENV PYTHONUNBUFFERED=1

# keep application content in a working directory
WORKDIR /app

# COPY requirements.txt requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir poetry
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-dev

# copy application code
COPY app/ ./app/
COPY config.py gunicorn_conf.py start.sh ./
RUN chmod +x start.sh

# run single-process uvicorn, for debug
# if packages are installed by pip, use the following command
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# if packages are installed by poetry, use the following command
# CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# run multi-process gunicorn, for production
CMD ["./start.sh"]

