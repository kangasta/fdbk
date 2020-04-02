import json
import logging
import os

from dateutil.parser import isoparse
from flask import Flask, request, send_from_directory

from fdbk import utils
from ._server_handlers import ServerHandlers


def generate_app(config=None, serve_cwd=True, log_level=logging.WARN):
    default_config = {
        "DBConnection": "DictConnection",
        "DBParameters": [],
        "AllowedActions": [
            "add_data",
            "add_topic",
            "get_comparison",
            "get_data",
            "get_latest",
            "get_overview",
            "get_summary",
            "get_topics",
            "get_topic"
        ],
        "ServeCWD": serve_cwd
    }

    if not config:
        config = default_config
    elif isinstance(config, str):
        with open(config, "r") as f:
            config = json.load(f)
    elif not isinstance(config, dict):
        raise ValueError("Input configuration not recognized.")

    static_folder = os.path.join(
        os.getcwd(), "static") if config["ServeCWD"] else None
    app = Flask(__name__, static_folder=static_folder)

    db_connection = utils.create_db_connection(
        config["DBConnection"], config["DBParameters"])

    handlers = ServerHandlers(db_connection, config)

    app.logger.setLevel(log_level)  # pylint: disable=no-member
    app.logger.info('Created "' +  # pylint: disable=no-member
                    config["DBConnection"] +
                    '" with parameters: ' +
                    str(config["DBParameters"]))

    # API

    if config["ServeCWD"]:
        @app.route('/')
        def index():
            return send_from_directory(os.getcwd(), 'index.html')

    @app.route('/topics', methods=['GET', 'POST'])
    def topics():
        if request.method == 'GET':
            return handlers.get_topics(request.args.get('type'))
        if request.method == 'POST':
            return handlers.add_topic()

    @app.route('/topics/<topic_id>', methods=['GET'])
    def topics_get(topic_id):
        return handlers.get_topic(topic_id)

    def _parse_param(param, parser):
        try:
            return isoparse(param)
        except Exception:
            return None

    @app.route('/topics/<topic_id>/data', methods=['GET', 'POST'])
    def data(topic_id):
        if request.method == 'GET':
            return handlers.get_data(
                topic_id,
                _parse_param(request.args.get('since'), isoparse),
                _parse_param(request.args.get('until'), isoparse),
                _parse_param(request.args.get('limit'), int))
        if request.method == 'POST':
            return handlers.add_data(topic_id)

    @app.route('/topics/<topic_id>/data/latest', methods=['GET', 'POST'])
    def latest(topic_id):
        return handlers.get_latest(topic_id)

    @app.route('/topics/<topic_id>/summary', methods=['GET'])
    def summary(topic_id):
        return handlers.get_summary(topic_id)

    @app.route('/comparison/<topic_ids>', methods=['GET'])
    def comparison(topic_ids):
        return handlers.get_comparison(topic_ids)

    @app.route('/comparison', methods=['GET'])
    def comparison_all():
        return handlers.get_comparison()

    @app.route('/overview', methods=['GET'])
    def overview():
        return handlers.get_overview()

    return app
