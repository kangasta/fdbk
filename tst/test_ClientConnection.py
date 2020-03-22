from datetime import datetime
from unittest import TestCase

from unittest.mock import Mock, patch

import requests

from fdbk import ClientConnection
from fdbk.server import generate_app

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
        self.__server = generate_app().test_client()

    def mock_requests_get(self, *args, **kwargs):
        response = self.__server.get(*args, **kwargs)
        return MockResponse(response.json, response.status_code)

    def mock_requests_post(self, *args, **kwargs):
        response = self.__server.post(*args, **kwargs)
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

    def test_fresh_server_returns_empty_response_or_error(self):
        c = ClientConnection("")
        with patch('requests.get', side_effect=self.mock_requests_get):
            self.assertEqual(c.get_topics(), [])

        # TODO: check that correct errors are raised
        with self.assertRaises(Exception):
            c.get_topic("topic_id")
        with self.assertRaises(Exception):
            c.get_data("topic_id")

    def test_add_topic_triggers_correct_call(self):
        c = ClientConnection("")
        with patch('requests.post', side_effect=self.mock_requests_post), patch('fdbk.DictConnection.add_topic', return_value="topic_id") as add_topic:
            c.add_topic("topic", type_str="test", add_id=False)
            add_topic.assert_called_with("topic", type_str="test", description="", fields=[], units=[], summary=[], visualization=[], metadata={}, form_submissions=False)

    def test_add_data_triggers_correct_call(self):
        c = ClientConnection("")
        with patch('requests.post', side_effect=self.mock_requests_post), \
            patch('fdbk.DictConnection.add_data') as add_data:
            c.add_data("topic", {"number": 3})
            add_data.assert_called_with("topic", {"number": 3})
