from datetime import datetime
from unittest import TestCase

try:
	from unittest.mock import Mock, patch
except ImportError:
	from mock import Mock, patch

from fdbk import ClientConnection
from fdbk.server import generate_app

class ClientConnectionTest(TestCase):
	def setUp(self):
		self.__server = generate_app().test_client()

	def mock_requests_get(self, *args, **kwargs):
		class MockResponse:
			def __init__(self, json_data, status_code):
				self.json_data = json_data
				self.status_code = status_code

			def json(self):
				return self.json_data

		response = self.__server.get(*args, **kwargs)
		return MockResponse(response.json, response.status_code)

	def mock_requests_post(self, *args, **kwargs):
		return self.__server.post(args[0], json=kwargs["data"])

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
			addTopic.assert_called_with("topic", type_str="test", description="", fields=[], units=[], summary=[], visualization=[], allow_api_submissions=True)

	def test_add_topic_triggers_correct_calls(self):
		c = ClientConnection("")
		with patch('requests.post', side_effect=self.mock_requests_post), \
			patch('fdbk.DictConnection.getTopic') as getTopic, \
			patch('fdbk.DictConnection.addData') as addData:
			c.addData("topic", {"number": 3})
			getTopic.assert_called_with("topic")
			addData.assert_called_with("topic", {"number": 3})



