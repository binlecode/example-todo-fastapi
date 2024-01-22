#
FROM python:3.10

# 
WORKDIR /code

# 
COPY ./requirements.txt /code/requirements.txt

# disable cache saving to reduce image size
RUN pip install --no-cache-dir -r /code/requirements.txt

# 
# COPY ./app /code/app
# COPY ./config.py /code/config.py
# COPY ./gunicorn_conf.py /code/gunicorn_conf.py
# COPY ./start.sh /code/start.sh
COPY ./app /code/app
COPY ./config.py /code/

# run gunicorn with multi-process, for production deployment
COPY ./gunicorn_conf.py ./start.sh /code/
RUN chmod +x /code/start.sh

# run uvicorn with single process (for debug, not for production)
# COPY ./start-uvicorn.sh /code/start-uvicorn.sh
# RUN chmod +x /code/start-uvicorn.sh

# start by cmd string
#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]

# start uvicorn with single process
# CMD ["./start-uvicorn.sh"]

# start multi-process gunicorn, for production deployment
CMD ["./start.sh"]
