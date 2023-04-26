
# 
FROM python:3.10

# 
WORKDIR /code

# 
COPY ./requirements.txt /code/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 
COPY ./app /code/app

# copy sqlite db
COPY ./sqlite.db /code/sqlite.db

# 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
