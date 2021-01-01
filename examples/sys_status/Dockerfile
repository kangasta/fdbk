FROM python:3-alpine

RUN apk add build-base linux-headers && \
    pip install fdbk fdbk_mongodb_plugin psutil && \
    apk del build-base

WORKDIR /app
COPY sys_status.py ./

ENTRYPOINT ["python", "sys_status.py"]
