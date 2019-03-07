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

	def test_summary_and_visualization_funcs_handle_empty_lists(self):
		summaries = ["average", "latest"]
		visualizations = ["horseshoe", "line"]

		for summary, visualization in zip(summaries, visualizations):
			summary_d = {"field":"number", "method": summary}
			visualization_d = {"field":"number", "method": visualization}

			C = DictConnection()
			topic_id = C.addTopic("topic", fields=["number"], summary=[summary_d], visualization=[visualization_d])

			C.getSummary(topic_id)

	def test_get_summary_produces_summary(self):
		summary_d = {"field":"number", "method":"average"}
		visualization_d = {"field":"number", "method":"horseshoe"}

		C = DictConnection()
		topic_id = C.addTopic("topic", description="description", fields=["number"], summary=[summary_d], visualization=[visualization_d])
		C.addData(topic_id, {"number": 3})
		C.addData(topic_id, {"number": 4})
		C.addData(topic_id, {"number": 2})
		summary = C.getSummary(topic_id)
		self.assertEqual(summary["topic"], "topic")
		self.assertEqual(summary["description"], "description")

		self.assertAlmostEqual(summary["summaries"][0]["value"], 3.0)
		self.assertEqual(summary["summaries"][0]["field"], "number")
		self.assertEqual(summary["summaries"][0]["type"], "average")

		self.assertEqual(summary["visualizations"], [{
			"type": "horseshoe",
			"field": "number",
			"topic_name": "topic",
			"labels": [2,3,4],
			"data":[1,1,1],
			"unit": None
		}])

	def test_get_summary_ignores_invalid_fields(self):
		summary_d = {"field":"number", "method":"average"}
		visualization_d = {"field":"number", "method":"horseshoe"}

		C = DictConnection()
		topic_id = C.addTopic("topic", description="description", fields=["letter"], summary=[summary_d], visualization=[visualization_d])
		C.addData(topic_id, {"letter": "a"})

		summary = C.getSummary(topic_id)
		self.assertEqual(summary["topic"], "topic")
		self.assertEqual(summary["description"], "description")

		self.assertEqual(len(summary["warnings"]), 2)
		self.assertEqual(len(summary["summaries"]), 0)
		self.assertEqual(len(summary["visualizations"]), 0)

	def test_get_summary_average_ignores_invalid_values(self):
		summary_d = {"field":"number", "method":"average"}

		C = DictConnection()
		topic_id = C.addTopic("topic", description="description", fields=["number"], summary=[summary_d])
		C.addData(topic_id, {"number": 3})
		C.addData(topic_id, {"number": None})
		C.addData(topic_id, {"number": "Not a number"})
		summary = C.getSummary(topic_id)
		self.assertEqual(summary["topic"], "topic")
		self.assertEqual(summary["description"], "description")

		self.assertAlmostEqual(summary["summaries"][0]["value"], 3.0)
		self.assertEqual(summary["summaries"][0]["field"], "number")
		self.assertEqual(summary["summaries"][0]["type"], "average")

	def test_line_visualization_gives_timestamps_in_utc(self):
		visualization_d = {"field":"number", "method":"line"}

		C = DictConnection()
		topic_id = C.addTopic("topic", description="description", fields=["number"], visualization=[visualization_d])
		C.addData(topic_id, {"number": 1})
		C.addData(topic_id, {"number": 2})
		C.addData(topic_id, {"number": 3})
		summary = C.getSummary(topic_id)

		self.assertEqual(summary["visualizations"][0]["field"], "number")
		self.assertEqual(summary["visualizations"][0]["type"], "line")
		iso8601z_re = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{6}Z"

		try: # Python 3
			self.assertRegex(summary["visualizations"][0]["labels"][0], iso8601z_re)
		except AttributeError: # Python 2
			self.assertRegexpMatches(summary["visualizations"][0]["labels"][0], iso8601z_re)

	def test_latest_summary_returns_latest_item(self):
		summary_d = {"field":"letter", "method":"latest"}

		C = DictConnection()
		topic_id = C.addTopic("topic", description="description", fields=["letter"], summary=[summary_d])
		C.addData(topic_id, {"letter": "a"})
		C.addData(topic_id, {"letter": "b"})
		C.addData(topic_id, {"letter": "c"})
		summary = C.getSummary(topic_id)

		self.assertEqual(summary["summaries"][0]["field"], "letter")
		self.assertEqual(summary["summaries"][0]["type"], "latest")
		self.assertEqual(summary["summaries"][0]["value"], "c")

	def test_get_summary_writes_warning_to_output_when_unsupported_method_requested(self):
		summary_d = {"field":"number", "method":"cow"}
		visualization_d = {"field":"number", "method":"moose"}

		C = DictConnection()
		topic_id = C.addTopic("topic", description="description", fields=["number"], summary=[summary_d], visualization=[visualization_d])
		C.addData(topic_id, {"number": 3})
		summary = C.getSummary(topic_id)
		self.assertEqual(summary["warnings"], [
			"The requested method 'cow' is not supported.",
			"The requested method 'moose' is not supported."
		])

	def test_get_latest_handles_empty_list(self):
		C = DictConnection()
		topic_id = C.addTopic("topic")
		with self.assertRaises(IndexError):
			C.getLatest(topic_id)

	def test_get_latest_returns_latest_data_element_for_topic(self):
		C = DictConnection()
		topic_id = C.addTopic("topic", description="description", fields=["number"])
		C.addData(topic_id, {"number": 3})
		C.addData(topic_id, {"number": 2})
		C.addData(topic_id, {"number": 1})

		latest = C.getLatest(topic_id)
		self.assertEqual(latest["number"], 1)

	def test_last_truthy_falsy_summary_returns_correct_timestamp(self):
		summary_l = [
			{"field":"onoff", "method":"last_truthy"},
			{"field":"onoff", "method":"last_falsy"}
		]

		C = DictConnection()
		topic_id = C.addTopic("topic", description="description", fields=["onoff"], summary=summary_l)
		for i in [False, True, False, True]:
			C.addData(topic_id, {"onoff": i})

		summary = C.getSummary(topic_id)
		data = C.getData(topic_id)

		self.assertEqual(summary["summaries"][0]["value"], data[3]["timestamp"])
		self.assertEqual(summary["summaries"][1]["value"], data[2]["timestamp"])

	def test_get_comparison_produces_comparison(self):
		visualization_d = {"field":"number", "method":"horseshoe"}

		topic_ids = []
		C = DictConnection()
		for i in range(3):
			topic_ids.append(
				C.addTopic(
					"topic_" + str(i),
					description="description",
					fields=["number"],
					visualization=[visualization_d]
			))
			C.addData(topic_ids[-1], {"number": 3})
			C.addData(topic_ids[-1], {"number": 4})
			C.addData(topic_ids[-1], {"number": 2})
		comparison = C.getComparison(topic_ids)
		self.assertEqual(comparison["topic_names"], ["topic_0", "topic_1", "topic_2"])
		self.assertEqual(comparison["fields"], ["number"])

		self.assertEqual(len(comparison["visualizations"]), 3)

	def test_get_overview_produces_overview(self):
		summary_d = {"field":"number", "method":"latest"}

		C = DictConnection()
		for i in range(3):
			topic_id = C.addTopic(
				"topic_" + str(i),
				description="description",
				fields=["number"],
				summary=[summary_d]
			)
			C.addData(topic_id, {"number": i})
		overview = C.getOverview()
		self.assertEqual(overview["topic_names"], ["topic_0", "topic_1", "topic_2"])
		self.assertEqual(overview["fields"], ["number"])

		self.assertEqual(len(overview["summaries"]), 3)

	def test_overview_and_comparison_include_units(self):
		summary_d = {"field":"number", "method":"latest"}
		visualization_d = {"field":"number", "method":"horseshoe"}
		units_d = {"field":"number", "unit":"scalar"}

		C = DictConnection()
		for i in range(3):
			topic_id = C.addTopic(
				"topic_" + str(i),
				description="description",
				fields=["number"],
				summary=[summary_d],
				visualization=[visualization_d],
				units=[units_d]
			)
			C.addData(topic_id, {"number": i})
		overview = C.getOverview()
		self.assertEqual(overview["topic_names"], ["topic_0", "topic_1", "topic_2"])
		self.assertEqual(overview["fields"], ["number"])

		self.assertEqual(len(overview["summaries"]), 3)
		self.assertEqual(overview["summaries"][0]["unit"], "scalar")