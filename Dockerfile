# Use the official Python image as a base image
FROM python:3.11-slim

# Set environment variables
# Prevents Python from writing .pyc files which are unnecessary in a container.
ENV PYTHONDONTWRITEBYTECODE=1
# Ensures that output is sent straight to the terminal without being buffered, which is useful for logging.
ENV PYTHONUNBUFFERED=1

# keep application content in a working directory
WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-root --without dev

# copy application code
COPY app/ ./app/
COPY config.py ./

# default to UPDATE_DB=1
ENV RESET_DB=0
ENV UPDATE_DB=1

# Run appliction in container, prefer single process per container.
# This assumes the pod resource limit on CPU is less than 1.0.
# To concurrent request scale, keep single process per container and increase 
# replica size.
# For cpu bound performance bottleneck, increase cpu limit to be close or equal
# to 1.0, there's no benefit to increase cpu limit beyond 1.0. If bottleneck 
# remains, consider a higer cpu machine type. 
CMD ["poetry", "run", "fastapi", "run", "--host", "0.0.0.0", "--port", "8000"]


