FROM python:3-alpine

RUN pip install fdbk

WORKDIR /app
COPY sys_status.py targets.json ./

ENTRYPOINT ["python", "net_status.py", "-f", "targets.json"]
