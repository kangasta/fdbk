from datetime import datetime
from unittest import TestCase

try:
	from unittest.mock import MagicMock, Mock, patch
except ImportError:
	from mock import MagicMock, Mock, patch

from fdbk import InfluxConnection

class InfluxConnectionTest(TestCase):
	def test_has_secondary_connection_for_topics_data(self):
		C = InfluxConnection('Invalid URL!')
		topic_id = C.addTopic('test_topic')
		self.assertEqual(len(C.getTopics()), 1)
		self.assertEqual(C.getTopic(topic_id)['name'], 'test_topic')

	@patch('fdbk.InfluxConnection.InfluxDBClientWrapper.write_points')
	def test_add_data_method_use_influx_python_api(self, write_mock):
		C = InfluxConnection('Invalid URL!')
		topic_id = C.addTopic('test_topic', fields=['number'])

		data = {'number': 3}
		C.addData(topic_id, {'number': 3})

		write_mock.assert_called_with([{
			'measurement': '',
			'tags': {
				'topic_id': topic_id
			},
			'fields': data
		}], database='default_db')
