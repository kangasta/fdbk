'''Development server handlers, interfaces not stable
'''


class ServerHandlers:
    def __init__(self, db_connection):
        self._db_connection = db_connection

    def add_topic(self, json_in):
        topic = json_in.pop("name", None)
        type_str = json_in.pop("type", None)
        if not topic:
            return {
                "error": "No 'topic' field in input data"
            }, 404

        try:
            topic_id = self._db_connection.add_topic(
                topic, type_str=type_str, **json_in)
        except KeyError as error:
            # Field not available in input data
            return {
                "error": str(error)
            }, 404
        except TypeError as error:
            return {
                "error": str(error)
            }, 400
        return {
            "topic_id": topic_id,
            "success": "Topic successfully added to DB"
        }, 200

    def add_data(self, topic_id, json_in):
        try:
            self._db_connection.add_data(topic_id, json_in)
        except KeyError as error:
            # Topic not defined
            return {
                "error": str(error)
            }, 404
        except ValueError as error:
            # Fields do not match with topic
            return {
                "error": str(error)
            }, 400
        return {
            "success": "Data successfully added to DB"
        }, 200

    def get_topics(self, type_=None):
        return self._db_connection.get_topics(type_), 200

    def get_topic(self, topic_id):
        try:
            topic_json = self._db_connection.get_topic(topic_id)
            return topic_json, 200
        except KeyError as error:
            return {
                "error": str(error)
            }, 404

    def get_data(self, topic_id, since=None, until=None, limit=None):
        try:
            data = self._db_connection.get_data(topic_id, since, until, limit)
            return data, 200
        except KeyError as error:
            return {
                "error": str(error)
            }, 404

    def get_latest(self, topic_id):
        try:
            data = self._db_connection.get_latest(topic_id)
            return data, 200
        except Exception as error:
            return {
                "error": str(error)
            }, 404

    def get_summary(self, topic_id):
        try:
            data = self._db_connection.get_summary(topic_id)
            return data, 200
        except KeyError as error:
            return {
                "error": str(error)
            }, 404

    def get_comparison(self, topic_ids=None):
        topic_ids_a = topic_ids.split(',') if topic_ids else None

        try:
            data = self._db_connection.get_comparison(topic_ids_a)
            return data, 200
        except KeyError as error:
            return {
                "error": str(error)
            }, 404

    def get_overview(self):
        try:
            data = self._db_connection.get_overview()
            return data, 200
        except KeyError as error:
            return {
                "error": str(error)
            }, 404
