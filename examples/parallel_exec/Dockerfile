FROM python:3-alpine

RUN pip install fdbk fdbk_mongodb_plugin

WORKDIR /app
COPY *.py ./

ENTRYPOINT ["python", "-um", "fdbk.builtin.parallel_exec"]
