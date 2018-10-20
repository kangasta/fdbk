from unittest import TestCase

try:
	from unittest.mock import Mock, patch
except ImportError:
	from mock import Mock, patch

from fdbk import DictConnection
from fdbk import DBConnection

class DBConnectionTest(TestCase):
	def test_abstract_methods_raise_not_implemented_error(self):
		C = DBConnection()
		with self.assertRaises(NotImplementedError):
			C.addTopic("topic")
		with self.assertRaises(NotImplementedError):
			C.addData("topic",None)
		with self.assertRaises(NotImplementedError):
			C.getTopics()
		with self.assertRaises(NotImplementedError):
			C.getTopic("topic")
		with self.assertRaises(NotImplementedError):
			C.getData("topic")

	def test_get_summary_produces_summary(self):
		C = DictConnection()
		C.addTopic("topic", description="description", fields=["number"], summary=["average"], visualization=["horseshoe"])
		C.addData("topic", {"number": 3})
		C.addData("topic", {"number": 4})
		C.addData("topic", {"number": 2})
		summary = C.getSummary("topic")
		self.assertEqual(summary["topic"], "topic")
		self.assertEqual(summary["description"], "description")

		self.assertAlmostEqual(summary["summaries"][0]["value"], 3.0)
		self.assertEqual(summary["summaries"][0]["field"], "number")
		self.assertEqual(summary["summaries"][0]["type"], "average")

		self.assertEqual(summary["visualizations"], [{
			"type": "horseshoe",
			"field": "number",
			"labels": [2,3,4],
			"data":[1,1,1]
		}])

	def test_get_summary_writes_warning_to_output_when_unsupported_method_requested(self):
		C = DictConnection()
		C.addTopic("topic", description="description", fields=["number"], summary=["cow"], visualization=["moose"])
		C.addData("topic", {"number": 3})
		summary = C.getSummary("topic")
		self.assertEqual(summary["warnings"], [
			"The requested summary method 'cow' is not supported.",
			"The requested visualization method 'moose' is not supported."
		])