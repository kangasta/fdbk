from datetime import datetime
from unittest import TestCase
from unittest.mock import Mock, patch

from freezegun import freeze_time
import requests

from fdbk import ClientConnection, DictConnection
from fdbk.server import generate_app
from fdbk.utils import CommonTest

class MockResponse(object):
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

    @property
    def ok(self):
        return self.status_code == requests.codes.ok


class ClientConnectionTest(TestCase):
    def setUp(self):
        self.connection = DictConnection()
        self.server = generate_app(db_connection=self.connection).test_client()

    def mock_requests_get(self, *args, **kwargs):
        response = self.server.get(*args, **kwargs)
        return MockResponse(response.json, response.status_code)

    def mock_requests_post(self, *args, **kwargs):
        response = self.server.post(*args, **kwargs)
        return MockResponse(response.json, response.status_code)

    def mock_requests_post_404(self, *args, **kwargs):
        return MockResponse(404, {"error": "Mocked 404"})

    def test_failing_add_calls_should_raise_RuntimeError(self):
        c = ClientConnection("")
        with patch('requests.post', side_effect=self.mock_requests_post_404):
            with self.assertRaises(RuntimeError):
                c.add_topic("topic")
            with self.assertRaises(RuntimeError):
                c.add_data("topic", {"number": 3})

    def test_add_and_get_data(self):
        with patch('requests.get', side_effect=self.mock_requests_get), \
            patch('requests.post', side_effect=self.mock_requests_post):
            C = ClientConnection("")

            data_tools = [
                {"field":"number", "method":"line"},
            ]

            self.assertEqual(len(C.get_topics()), 0)

            with self.assertRaises(RuntimeError):
                C.get_topic('Not found')

            template_id = C.add_topic("template", type_str="template", fields=["number"], data_tools=data_tools)
            topic_id = C.add_topic("topic")

            with self.assertRaises(RuntimeError):
                topic_id = C.add_topic("topic", template="template", id_str=topic_id)

            topic_id = C.add_topic("topic", template="template", id_str=topic_id, overwrite=True)

            self.assertEqual(len(C.get_topics()), 2)
            self.assertEqual(len(C.get_topics("template")), 1)
            self.assertEqual(len(C.get_topics(template="template")), 1)
            self.assertEqual(len(C.get_data(topic_id)), 0)

            topic_d = C.get_topic(topic_id)
            self.assertEqual(topic_d["fields"], ["number"])

            dt_jan_first = datetime(2020, 1, 1, 1, 0)
            with freeze_time(dt_jan_first):
                timestamp = C.add_data(topic_id, {"number": 3})
            self.assertEqual(timestamp, f"{dt_jan_first.isoformat()}Z")

            with self.assertRaises(RuntimeError):
                with freeze_time(dt_jan_first):
                    C.add_data(topic_id, {"number": 5})

            with freeze_time(dt_jan_first):
                timestamp = C.add_data(topic_id, {"number": 7}, overwrite=True)

            data = C.get_data(topic_id)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["number"], 7)

            statistics = C.get_overview()["statistics"]
            self.assertEqual(len(statistics), 1)
