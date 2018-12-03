from datetime import datetime
from unittest import TestCase

try:
	from unittest.mock import Mock, patch
except ImportError:
	from mock import Mock, patch

from fdbk import ClientConnection
from fdbk.server import generate_app

class MockResponse(object):
	def __init__(self, json_data, status_code):
		self.json_data = json_data
		self.status_code = status_code

	def json(self):
		return self.json_data

class ClientConnectionTest(TestCase):
	def setUp(self):
		self.__server = generate_app().test_client()

	def mock_requests_get(self, *args, **kwargs):
		response = self.__server.get(*args, **kwargs)
		return MockResponse(response.json, response.status_code)

	def mock_requests_post(self, *args, **kwargs):
		return self.__server.post(*args, **kwargs)

	def mock_requests_post_404(self, *args, **kwargs):
		return MockResponse(404, {"error": "Mocked 404"})

	def test_failing_add_calls_should_raise_RuntimeError(self):
		c = ClientConnection("")
		with patch('requests.post', side_effect=self.mock_requests_post_404):
			with self.assertRaises(RuntimeError):
				c.addTopic("topic")
			with self.assertRaises(RuntimeError):
				c.addData("topic", {"number": 3})

	def test_fresh_server_returns_empty_response_or_error(self):
		c = ClientConnection("")
		with patch('requests.get', side_effect=self.mock_requests_get):
			self.assertEqual(c.getTopics(), [])

		# TODO: check that correct errors are raised
		with self.assertRaises(Exception):
			c.getTopic("topic")
		with self.assertRaises(Exception):
			c.getData("topic")

	def test_add_topic_triggers_correct_call(self):
		c = ClientConnection("")
		with patch('requests.post', side_effect=self.mock_requests_post), patch('fdbk.DictConnection.addTopic') as addTopic:
			c.addTopic("topic", "test")
			addTopic.assert_called_with("topic", type_str="test", description="", fields=[], units=[], summary=[], visualization=[], form_submissions=False)

	def test_add_data_triggers_correct_call(self):
		c = ClientConnection("")
		with patch('requests.post', side_effect=self.mock_requests_post), \
			patch('fdbk.DictConnection.addData') as addData:
			c.addData("topic", {"number": 3})
			addData.assert_called_with("topic", {"number": 3})
