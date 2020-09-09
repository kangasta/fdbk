FROM python:3-alpine

RUN pip install fdbk fdbk_mongodb_plugin

WORKDIR /app
COPY net_status.py targets.json ./

ENTRYPOINT ["python", "net_status.py", "-f", "targets.json"]
