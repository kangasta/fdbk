from flask import jsonify, request


class ServerHandlers:
    def __init__(self, db_connection, config):
        self.__db_connection = db_connection
        self.__config = config

        self.__invalid_token_json = {
            "error": "Token not recognized"
        }

        self.__action_not_allowed_json = {
            "error": "Action not allowed"
        }

    def add_topic(self):
        if "add_topic" not in self.__config["AllowedActions"]:
            return jsonify(self.__action_not_allowed_json), 403
        if "AddTokens" in self.__config and self.__config["AddTokens"] and (
                "token" not in request.args or
                request.args["token"] not in self.__config["AddTokens"]):
            return jsonify(self.__invalid_token_json), 403
        try:
            json_in = request.get_json()
        except BaseException:
            return jsonify({
                "error": "No topic data provided in request"
            }), 404

        topic = json_in.pop("name", None)
        type_str = json_in.pop("type", None)
        if not topic:
            return jsonify({
                "error": "No 'topic' field in input data"
            }), 404

        try:
            topic_id = self.__db_connection.add_topic(
                topic, type_str=type_str, **json_in)
        except KeyError as error:
            # Field not available in input data
            return jsonify({
                "error": str(error)
            }), 404
        except TypeError as error:
            return jsonify({
                "error": str(error)
            }), 400
        return jsonify({
            "topic_id": topic_id,
            "success": "Topic successfully added to DB"
        })

    def add_data(self, topic_id):
        if "add_data" not in self.__config["AllowedActions"]:
            return jsonify(self.__action_not_allowed_json), 403
        if "AddTokens" in self.__config and self.__config["AddTokens"] and (
                "token" not in request.args or
                request.args["token"] not in self.__config["AddTokens"]):
            return jsonify(self.__invalid_token_json), 403

        try:
            json_in = request.get_json()
        except BaseException:
            return jsonify({
                "error": "No topic data provided in request"
            }), 404
        try:
            self.__db_connection.add_data(topic_id, json_in)
        except KeyError as error:
            # Topic not defined
            return jsonify({
                "error": str(error)
            }), 404
        except ValueError as error:
            # Fields do not match with topic
            return jsonify({
                "error": str(error)
            }), 400
        return jsonify({
            "success": "Data successfully added to DB"
        })

    def get_topics(self, type_=None):
        if "get_topics" not in self.__config["AllowedActions"]:
            return jsonify(self.__action_not_allowed_json), 403
        return jsonify(self.__db_connection.get_topics(type_))

    def get_topic(self, topic_id):
        if "get_topic" not in self.__config["AllowedActions"]:
            return jsonify(self.__action_not_allowed_json), 403
        try:
            topic_json = self.__db_connection.get_topic(topic_id)
            return jsonify(topic_json)
        except KeyError as error:
            return jsonify({
                "error": str(error)
            }), 404

    def get_data(self, topic_id, since=None, until=None, limit=None):
        if "get_data" not in self.__config["AllowedActions"]:
            return jsonify(self.__action_not_allowed_json), 403
        try:
            data = self.__db_connection.get_data(topic_id, since, until, limit)
            return jsonify(data)
        except KeyError as error:
            return jsonify({
                "error": str(error)
            }), 404

    def get_latest(self, topic_id):
        if "get_latest" not in self.__config["AllowedActions"]:
            return jsonify(self.__action_not_allowed_json), 403
        try:
            data = self.__db_connection.get_latest(topic_id)
            return jsonify(data)
        except Exception as error:
            return jsonify({
                "error": str(error)
            }), 404

    def get_summary(self, topic_id):
        if "get_summary" not in self.__config["AllowedActions"]:
            return jsonify(self.__action_not_allowed_json), 403
        try:
            data = self.__db_connection.get_summary(topic_id)
            return jsonify(data)
        except KeyError as error:
            return jsonify({
                "error": str(error)
            }), 404

    def get_comparison(self, topic_ids=None):
        if "get_comparison" not in self.__config["AllowedActions"]:
            return jsonify(self.__action_not_allowed_json), 403

        topic_ids_a = topic_ids.split(',') if topic_ids else None

        try:
            data = self.__db_connection.get_comparison(topic_ids_a)
            return jsonify(data)
        except KeyError as error:
            return jsonify({
                "error": str(error)
            }), 404

    def get_overview(self):
        if "get_overview" not in self.__config["AllowedActions"]:
            return jsonify(self.__action_not_allowed_json), 403
        try:
            data = self.__db_connection.get_overview()
            return jsonify(data)
        except KeyError as error:
            return jsonify({
                "error": str(error)
            }), 404
