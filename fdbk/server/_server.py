'''Development server, interfaces not stable
'''

import logging

from flask import Flask, jsonify, request

from fdbk.utils import create_db_connection
from ._server_handlers import ServerHandlers


def generate_app(db_plugin, db_parameters, log_level=logging.WARN):
    app = Flask(__name__)

    db_connection = create_db_connection(
        db_plugin, db_parameters)

    handlers = ServerHandlers(db_connection)

    app.logger.setLevel(log_level)  # pylint: disable=no-member
    app.logger.info('Created "' +  # pylint: disable=no-member
                    db_plugin +
                    '" with parameters: ' +
                    str(db_parameters))

    def _jsonify(response):
        data, code = response
        return jsonify(data), code

    @app.route('/topics', methods=['GET', 'POST'])
    def topics():
        if request.method == 'GET':
            return _jsonify(handlers.get_topics(request.args.get('type')))
        if request.method == 'POST':
            try:
                json_in = request.get_json()
            except BaseException:
                return jsonify({
                    "error": "No topic data provided in request"
                }), 404
            return _jsonify(handlers.add_topic(json_in))

    @app.route('/topics/<topic_id>', methods=['GET'])
    def topics_get(topic_id):
        return _jsonify(handlers.get_topic(topic_id))

    @app.route('/topics/<topic_id>/data', methods=['GET', 'POST'])
    def data(topic_id):
        if request.method == 'GET':
            return _jsonify(handlers.get_data(
                topic_id,
                request.args))
        if request.method == 'POST':
            try:
                json_in = request.get_json()
            except BaseException:
                return jsonify({
                    "error": "No topic data provided in request"
                }), 404
            return _jsonify(handlers.add_data(topic_id, json_in))

    @app.route('/topics/<topic_id>/data/latest', methods=['GET', 'POST'])
    def latest(topic_id):
        return _jsonify(handlers.get_latest(topic_id))

    @app.route('/topics/<topic_id>/summary', methods=['GET'])
    def summary(topic_id):
        return _jsonify(handlers.get_summary(
            topic_id, request.args))

    @app.route('/comparison/<topic_ids>', methods=['GET'])
    def comparison(topic_ids):
        return _jsonify(handlers.get_comparison(topic_ids, request.args))

    @app.route('/comparison', methods=['GET'])
    def comparison_all():
        return _jsonify(handlers.get_comparison(query_args=request.args))

    @app.route('/overview/<type>', methods=['GET'])
    def overview(type_):
        return _jsonify(handlers.get_overview(type_, request.args))

    @app.route('/overview', methods=['GET'])
    def overview_all():
        return _jsonify(handlers.get_overview(query_args=request.args))

    return app
