from unittest import TestCase

try:
	from unittest.mock import Mock, patch
except ImportError:
	from mock import Mock, patch

from fdbk import DictConnection

class DictConnectionTest(TestCase):
	def test_cannot_add_topic_twice(self):
		C = DictConnection()
		C.addTopic("topic")
		with self.assertRaises(KeyError):
			C.addTopic("topic")

	def test_add_topic_affects_get_topic_s_output(self):
		C = DictConnection()
		C.addTopic("topic")
		self.assertEqual(C.getTopic("topic")["topic"], "topic")
		self.assertEqual(C.getTopics()[0]["topic"], "topic")
		self.assertEqual(len(C.getTopics()), 1)

	def test_cannot_add_data_to_undefined_topic(self):
		C = DictConnection()
		with self.assertRaises(KeyError):
			C.addData("topic", {"key": "value"})

	def test_cannot_add_data_with_non_matching_number_of_fields(self):
		C = DictConnection()
		C.addTopic("topic", "description", ["number"])
		with self.assertRaises(ValueError):
			C.addData("topic", {"key1": "value1", "key2": "value2"})

	def test_cannot_add_data_with_non_matching_fields(self):
		C = DictConnection()
		C.addTopic("topic", "description", ["number"])
		with self.assertRaises(ValueError):
			C.addData("topic", {"key": "value"})

	def test_add_data_affects_get_data_output(self):
		C = DictConnection()
		C.addTopic("topic", "description", ["number"])
		C.addData("topic", {"number": 3})
		self.assertEqual(C.getData("topic")[0]["number"], 3)
		self.assertEqual(len(C.getData("topic")), 1)

	def test_cannot_get_undefined_topic(self):
		C = DictConnection()
		with self.assertRaises(KeyError):
			C.getTopic("topic")

	def test_cannot_get_data_of_undefined_topic(self):
		C = DictConnection()
		with self.assertRaises(KeyError):
			C.getData("topic")
