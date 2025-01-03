FROM python:3.11.8

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# copy app source code
COPY app app
COPY config.py gunicorn_conf.py start.sh ./
RUN chmod +x start.sh

# run uvicorn with single process (for debug, not for production)
# COPY ./start-uvicorn.sh /code/start-uvicorn.sh
# RUN chmod +x /code/start-uvicorn.sh

# start by cmd string
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
# CMD ["./start-uvicorn.sh"]

# start multi-process gunicorn, for production deployment
CMD ["./start.sh"]
