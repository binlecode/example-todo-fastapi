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
COPY ./config.py /code/config.py
COPY ./gunicorn_conf.py /code/gunicorn_conf.py

# copy start scripts
COPY ./start.sh /code/start.sh
RUN chmod +x /code/start.sh

COPY ./start-uvicorn.sh /code/start-uvicorn.sh
RUN chmod +x /code/start-uvicorn.sh

# set default db init mode to create/update
ENV UPDATE_DB=1

# start by cmd string
#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]

# start uvicorn with single process
# CMD ["./start-uvicorn.sh"]

# start multi-process gunicorn, for production deployment
CMD ["./start.sh"]
