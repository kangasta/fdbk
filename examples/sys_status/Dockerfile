FROM python:3-alpine

RUN pip install fdbk

WORKDIR /app
COPY sys_status.py ./

ENTRYPOINT ["python", "sys_status.py"]
