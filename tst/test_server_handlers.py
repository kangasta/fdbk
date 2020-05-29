from datetime import datetime
from dateutil.tz import tzutc

from unittest import TestCase
from unittest.mock import Mock, patch

from fdbk import DictConnection
from fdbk.server import parse_filter_parameters, ServerHandlers

class ServerHandlersTest(TestCase):
    def _assert_status(self, expected_status, function, *args, **kwargs):
        data, status = function(*args, **kwargs)
        self.assertEqual(status, expected_status)
        return data

    def _create_topic(self, server_handlers, topic):
        response = self._assert_status(200, server_handlers.add_topic, topic)
        return response.get("topic_id")

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
        self._assert_status(400, s.add_topic, {})

    def test_add_topic_returns_400_when_topic_data_is_invalid(self):
        s = ServerHandlers(DictConnection())
        self._assert_status(400, s.add_topic, dict(name="test", fields=123))

    def test_add_topic_returns_200_on_success(self):
        s = ServerHandlers(DictConnection())
        self._assert_status(200, s.add_topic, dict(name="topic"))

    def test_add_data_get_data_and_get_latest_and_get_summary(self):
        s = ServerHandlers(DictConnection())

        self._assert_status(404, s.get_latest, None)

        topic_id = self._create_topic(s, dict(name="topic", fields=["number"]))

        self._assert_status(404, s.get_latest, topic_id)

        response = self._assert_status(200, s.get_data, topic_id, {})
        self.assertEqual(len(response), 0)

        self._assert_status(200, s.add_data, topic_id, dict(number=3))

        response = self._assert_status(200, s.get_latest, topic_id)
        self.assertEqual(response.get("number"), 3)

        self._assert_status(200, s.add_data, topic_id, dict(number=3))

        response = self._assert_status(200, s.get_data, topic_id, {})
        self.assertEqual(len(response), 2)

        self._assert_status(200, s.get_summary, topic_id, {})

    def test_add_data_validations(self):
        s = ServerHandlers(DictConnection())

        self._assert_status(404, s.add_data, None, dict(number=3))

        topic_id = self._create_topic(s, dict(name="topic", fields=["number"]))
        self._assert_status(400, s.add_data, topic_id, dict(letter="a"))

    def test_get_topic(self):
        s = ServerHandlers(DictConnection())

        self._assert_status(404, s.get_topic, None)
        topic_id = self._create_topic(s, dict(name="topic", fields=["number"]))
        self._assert_status(200, s.get_topic, topic_id)
