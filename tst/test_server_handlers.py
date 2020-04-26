from datetime import datetime
from dateutil.tz import tzutc

from unittest import TestCase
from unittest.mock import Mock, patch

from fdbk import DictConnection
from fdbk.server import parse_filter_parameters, ServerHandlers

class ServerHandlersTest(TestCase):
    def test_parse_filter_parameters(self):
        params = dict(
            since="2020-04-26T19:18:14.123456Z",
            until="2020-04-26T19:18:14.123456Z",
            limit="123",
            asd="asd"
        )

        parsed = parse_filter_parameters(params)
        self.assertEqual(parsed.get("since"), datetime(2020,4,26,19,18,14,123456, tzutc()))
        self.assertEqual(parsed.get("until"), datetime(2020,4,26,19,18,14,123456, tzutc()))
        self.assertEqual(parsed.get("limit"), 123)
        self.assertIsNone(parsed.get("asd"))

    def test_parse_filter_parameters_catches_parsing_error(self):
        parsed = parse_filter_parameters(dict(limit="cow"))
        self.assertIsNone(parsed.get("limit"))

    def test_add_topic_returns_400_when_topic_name_missing(self):
        s = ServerHandlers(DictConnection())

        _, status = s.add_topic({})
        self.assertEqual(status, 400)

    def test_add_topic_returns_400_when_topic_data_is_invalid(self):
        s = ServerHandlers(DictConnection())

        response, status = s.add_topic(dict(name="test", fields=123))
        self.assertEqual(status, 400)

    def test_add_topic_returns_200_on_success(self):
        s = ServerHandlers(DictConnection())

        _, status = s.add_topic(dict(name="topic"))
        self.assertEqual(status, 200)

    def test_add_data_and_get_latest(self):
        s = ServerHandlers(DictConnection())

        _, status = s.get_latest(None)
        self.assertEqual(status, 404)

        response, status = s.add_topic(dict(name="topic", fields=["number"]))
        self.assertEqual(status, 200)
        topic_id = response.get("topic_id")

        _, status = s.get_latest(topic_id)
        self.assertEqual(status, 404)

        _, status = s.add_data(topic_id, dict(number=3))
        self.assertEqual(status, 200)

        response, status = s.get_latest(topic_id)
        self.assertEqual(status, 200)
        self.assertEqual(response.get("number"), 3)

    def test_add_data_validations(self):
        s = ServerHandlers(DictConnection())

        _, status = s.add_data(None, dict(number=3))
        self.assertEqual(status, 404)

        response, status = s.add_topic(dict(name="topic", fields=["number"]))
        self.assertEqual(status, 200)
        topic_id = response.get("topic_id")

        _, status = s.add_data(topic_id, dict(letter="a"))
        self.assertEqual(status, 400)

    def test_get_topic(self):
        s = ServerHandlers(DictConnection())

        _, status = s.get_topic(None)
        self.assertEqual(status, 404)

        response, status = s.add_topic(dict(name="topic", fields=["number"]))
        self.assertEqual(status, 200)
        topic_id = response.get("topic_id")

        _, status = s.get_topic(topic_id)
        self.assertEqual(status, 200)
