'''Development server handlers, interfaces not stable
'''

from dateutil.parser import isoparse


def _parse_param(param, parser):
    try:
        return parser(param)
    except Exception:
        return None


def parse_filter_parameters(args, include_aggregate=False):
    query = dict(
        since=_parse_param(args.get('since'), isoparse),
        until=_parse_param(args.get('until'), isoparse),
        limit=_parse_param(args.get('limit'), int)
    )

    if not include_aggregate:
        return query

    aggregate = dict(
        aggregate_to=_parse_param(args.get('aggregate_to'), int),
        aggregate_with=args.get('aggregate_with')
    )

    return {**aggregate, **query}


def _get_response_or_not_found(function, args, kwargs=None):
    if not kwargs:
        kwargs = {}

    try:
        data = function(*args, **kwargs)
        return data, 200
    except Exception as error:
        return {
            "error": str(error)
        }, 404


def _get_overwrite(query_args):
    if not query_args:
        return False

    overwrite_str = query_args.get("overwrite")
    if not overwrite_str:
        return False

    return overwrite_str.lower() == "true"


def _get_topics_parameters(query_args):
    if not query_args:
        return []

    return query_args.get('type'), query_args.get('template')


class ServerHandlers:
    def __init__(self, db_connection):
        self._db_connection = db_connection

    def add_topic(self, json_in, query_args=None):
        overwrite = _get_overwrite(query_args)
        topic = json_in.pop("name", None)
        id_str = json_in.pop("id", None)
        type_str = json_in.pop("type", None)
        if not topic:
            return {
                "error": "No 'topic' field in input data"
            }, 400

        try:
            topic_id = self._db_connection.add_topic(
                topic,
                id_str=id_str,
                type_str=type_str,
                overwrite=overwrite,
                **json_in)
        except Exception as error:
            return {
                "error": str(error)
            }, 400
        return {
            "topic_id": topic_id,
            "success": "Topic successfully added to DB"
        }, 200

    def add_data(self, topic_id, json_in, query_args=None):
        overwrite = _get_overwrite(query_args)
        try:
            timestamp = self._db_connection.add_data(
                topic_id, json_in, overwrite=overwrite)
        except KeyError as error:
            # Topic not defined
            return {
                "error": str(error)
            }, 404
        except (ValueError, AssertionError,) as error:
            # Fields do not match with topic or duplicate timestamp
            return {
                "error": str(error)
            }, 400
        return {
            "timestamp": timestamp,
            "success": "Data successfully added to DB"
        }, 200

    def get_topics(self, query_args=None):
        params = _get_topics_parameters(query_args)
        return self._db_connection.get_topics(*params), 200

    def get_topic(self, topic_id):
        return _get_response_or_not_found(
            self._db_connection.get_topic, (topic_id,))

    def get_data(self, topic_id, query_args):
        return _get_response_or_not_found(
            self._db_connection.get_data,
            (topic_id,),
            parse_filter_parameters(query_args))

    def get_latest(self, topic_id):
        return _get_response_or_not_found(
            self._db_connection.get_latest, (topic_id,))

    def get_summary(self, topic_id, query_args):
        return _get_response_or_not_found(
            self._db_connection.get_summary,
            (topic_id,),
            parse_filter_parameters(query_args, include_aggregate=True))

    def get_comparison(self, topic_ids=None, query_args=None):
        topic_ids_a = topic_ids.split(',') if topic_ids else None
        if not query_args:
            query_args = {}

        try:
            params = parse_filter_parameters(
                query_args, include_aggregate=True)
            data = self._db_connection.get_overview(
                topic_ids_a, **params)
            return data, 200
        except KeyError as error:
            return {
                "error": str(error)
            }, 404

    def get_overview(self, template=None, query_args=None):
        if not query_args:
            query_args = {}

        try:
            params = parse_filter_parameters(
                query_args, include_aggregate=True)
            data = self._db_connection.get_overview(
                template=template, **params)
            return data, 200
        except KeyError as error:
            return {
                "error": str(error)
            }, 404
