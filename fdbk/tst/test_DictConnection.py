from unittest import TestCase

try:
	from unittest.mock import Mock, patch
except ImportError:
	from mock import Mock, patch

from fdbk import DictConnection

from common_tests import tests

class DictConnectionTest(TestCase):
	def test_run_common_tests(self,):
		for test in tests:
			C = DictConnection()
			test(self, C)

'''
Common tests:
	def test_add_topic_affects_get_topic_s_output(self):
		C = DictConnection()
		common_tests.add_topic_affects_get_topic_output(self, C)

	def test_cannot_add_data_to_undefined_topic(self):
		C = DictConnection()
		with self.assertRaises(KeyError):
			C.addData("topic_id", {"key": "value"})

	def test_cannot_add_data_with_non_matching_number_of_fields(self):
		C = DictConnection()
		topic_id = C.addTopic("topic", description="description", fields=["number"])
		with self.assertRaises(ValueError):
			C.addData(topic_id, {"key1": "value1", "key2": "value2"})

	def test_cannot_add_data_with_non_matching_fields(self):
		C = DictConnection()
		topic_id = C.addTopic("topic", description="description", fields=["number"])
		with self.assertRaises(ValueError):
			C.addData(topic_id, {"key": "value"})

	def test_add_data_affects_get_data_output(self):
		C = DictConnection()
		common_tests.add_data_affects_get_data_output(self, C)

	def test_cannot_get_undefined_topic(self):
		C = DictConnection()
		with self.assertRaises(KeyError):
			C.getTopic("topic_id")

	def test_cannot_get_data_of_undefined_topic(self):
		C = DictConnection()
		with self.assertRaises(KeyError):
			C.getData("topic_id")
'''
