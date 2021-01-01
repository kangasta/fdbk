FROM python:3-alpine

RUN pip install fdbk fdbk_mongodb_plugin flask_cors

ENTRYPOINT ["fdbk-server"]
CMD ["--help"]
