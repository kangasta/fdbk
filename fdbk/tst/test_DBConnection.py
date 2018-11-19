from datetime import datetime
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
		summary_d = {"field":"number", "method":"average"}
		visualization_d = {"field":"number", "method":"horseshoe"}

		C = DictConnection()
		C.addTopic("topic", description="description", fields=["number"], summary=[summary_d], visualization=[visualization_d])
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

	def test_get_summary_ignores_invalid_fields(self):
		summary_d = {"field":"number", "method":"average"}
		visualization_d = {"field":"number", "method":"horseshoe"}

		C = DictConnection()
		C.addTopic("topic", description="description", fields=["letter"], summary=[summary_d], visualization=[visualization_d])
		C.addData("topic", {"letter": "a"})

		summary = C.getSummary("topic")
		self.assertEqual(summary["topic"], "topic")
		self.assertEqual(summary["description"], "description")

		self.assertEqual(len(summary["warnings"]), 2)
		self.assertEqual(len(summary["summaries"]), 0)
		self.assertEqual(len(summary["visualizations"]), 0)

	def test_get_summary_average_ignores_invalid_values(self):
		summary_d = {"field":"number", "method":"average"}

		C = DictConnection()
		C.addTopic("topic", description="description", fields=["number"], summary=[summary_d])
		C.addData("topic", {"number": 3})
		C.addData("topic", {"number": None})
		C.addData("topic", {"number": "Not a number"})
		summary = C.getSummary("topic")
		self.assertEqual(summary["topic"], "topic")
		self.assertEqual(summary["description"], "description")

		self.assertAlmostEqual(summary["summaries"][0]["value"], 3.0)
		self.assertEqual(summary["summaries"][0]["field"], "number")
		self.assertEqual(summary["summaries"][0]["type"], "average")

	def test_line_visualization_gives_timestamps_in_utc(self):
		visualization_d = {"field":"number", "method":"line"}

		C = DictConnection()
		C.addTopic("topic", description="description", fields=["number"], visualization=[visualization_d])
		C.addData("topic", {"number": 1})
		C.addData("topic", {"number": 2})
		C.addData("topic", {"number": 3})
		summary = C.getSummary("topic")

		self.assertEqual(summary["visualizations"][0]["field"], "number")
		self.assertEqual(summary["visualizations"][0]["type"], "line")
		self.assertRegex(summary["visualizations"][0]["labels"][0], r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{6}Z")

	def test_latest_summary_returns_latest_item(self):
		summary_d = {"field":"letter", "method":"latest"}

		C = DictConnection()
		C.addTopic("topic", description="description", fields=["letter"], summary=[summary_d])
		C.addData("topic", {"letter": "a"})
		C.addData("topic", {"letter": "b"})
		C.addData("topic", {"letter": "c"})
		summary = C.getSummary("topic")

		self.assertEqual(summary["summaries"][0]["field"], "letter")
		self.assertEqual(summary["summaries"][0]["type"], "latest")
		self.assertEqual(summary["summaries"][0]["value"], "c")

	def test_get_summary_writes_warning_to_output_when_unsupported_method_requested(self):
		summary_d = {"field":"number", "method":"cow"}
		visualization_d = {"field":"number", "method":"moose"}

		C = DictConnection()
		C.addTopic("topic", description="description", fields=["number"], summary=[summary_d], visualization=[visualization_d])
		C.addData("topic", {"number": 3})
		summary = C.getSummary("topic")
		self.assertEqual(summary["warnings"], [
			"The requested summary method 'cow' is not supported.",
			"The requested visualization method 'moose' is not supported."
		])