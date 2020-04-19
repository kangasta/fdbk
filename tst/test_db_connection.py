from datetime import datetime
from unittest import TestCase

from unittest.mock import Mock, patch

from jsonschema.exceptions import ValidationError

from fdbk import DictConnection
from fdbk import DBConnection

class DBConnectionTest(TestCase):
    def test_abstract_methods_raise_not_implemented_error(self):
        C = DBConnection()
        with self.assertRaises(NotImplementedError):
            C.add_topic("topic")
        with self.assertRaises(NotImplementedError):
            C.add_data("topic",None)
        with self.assertRaises(NotImplementedError):
            C.get_topics()
        with self.assertRaises(NotImplementedError):
            C.get_topic("topic")
        with self.assertRaises(NotImplementedError):
            C.get_data("topic")

    def test_topic_is_validated_on_creation(self):
        data_tools_d = {"field":"number", "method":"average"}

        C = DictConnection()
        with self.assertRaises(ValidationError):
            C.add_topic("topic", description="description", fields=["number"], data_tools=data_tools_d)


    def test_get_summary_produces_summary(self):
        types = ("doughnut", "pie",)

        data_tools = [dict(field="number", method=_type) for _type in types] + [{"field":"number", "method":"average"}]

        C = DictConnection()
        topic_id = C.add_topic("topic", description="description", fields=["number"], data_tools=data_tools)
        C.add_data(topic_id, {"number": 3})
        C.add_data(topic_id, {"number": 4})
        C.add_data(topic_id, {"number": 2})
        summary = C.get_summary(topic_id)
        self.assertEqual(summary["topic"], "topic")
        self.assertEqual(summary["description"], "description")

        statistics = summary["statistics"]
        value = next(i for i in statistics if i.get("type") == "value").get("payload")
        self.assertAlmostEqual(value["value"], 3.0)
        self.assertEqual(value["field"], "number")
        self.assertEqual(value["type"], "average")

        charts = [i.get("payload") for i in statistics if i.get("type") == "chart"]
        self.assertEqual(charts, [{
            "field": "number",
            "type": type_,
            "data": {"datasets": [{"data": [1,1,1], "label": "topic"}], "labels": [2,3,4],}
        } for type_ in types])

    def test_get_summary_ignores_invalid_fields(self):
        data_tools = [
            {"field":"number", "method":"average"},
            {"field":"number", "method":"doughnut"},
        ]

        C = DictConnection()
        topic_id = C.add_topic("topic", description="description", fields=["letter"], data_tools=data_tools)
        C.add_data(topic_id, {"letter": "a"})

        summary = C.get_summary(topic_id)
        self.assertEqual(summary["topic"], "topic")
        self.assertEqual(summary["description"], "description")

        self.assertEqual(len(summary["warnings"]), 2)
        self.assertEqual(len(summary["statistics"]), 0)

    def test_get_summary_average_ignores_invalid_values(self):
        data_tools = [{"field":"number", "method":"average"}]

        C = DictConnection()
        topic_id = C.add_topic("topic", description="description", fields=["number"], data_tools=data_tools)
        C.add_data(topic_id, {"number": 3})
        C.add_data(topic_id, {"number": None})
        C.add_data(topic_id, {"number": "Not a number"})
        summary = C.get_summary(topic_id)
        self.assertEqual(summary["topic"], "topic")
        self.assertEqual(summary["description"], "description")

        value = summary["statistics"][0]["payload"]
        self.assertAlmostEqual(value["value"], 3.0)
        self.assertEqual(value["field"], "number")
        self.assertEqual(value["type"], "average")

    def test_line_visualization_gives_timestamps_in_utc(self):
        data_tools = [{"field":"number", "method":"line"}]

        C = DictConnection()
        topic_id = C.add_topic("topic", description="description", fields=["number"], data_tools=data_tools)
        C.add_data(topic_id, {"number": 1})
        C.add_data(topic_id, {"number": 2})
        C.add_data(topic_id, {"number": 3})
        summary = C.get_summary(topic_id)

        chart = summary["statistics"][0]["payload"]
        self.assertEqual(chart["field"], "number")
        self.assertEqual(chart["type"], "line")

        iso8601z_re = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{6}Z"
        field_to_test = chart["data"]["datasets"][0]["data"][0]["x"]

        self.assertRegex(field_to_test, iso8601z_re)

    def test_latest_summary_returns_latest_item(self):
        data_tools = [{"field":"letter", "method":"latest"}]

        C = DictConnection()
        topic_id = C.add_topic("topic", description="description", fields=["letter"], data_tools=data_tools)
        C.add_data(topic_id, {"letter": "a"})
        C.add_data(topic_id, {"letter": "b"})
        C.add_data(topic_id, {"letter": "c"})
        summary = C.get_summary(topic_id)

        value = summary["statistics"][0]["payload"]
        self.assertEqual(value["field"], "letter")
        self.assertEqual(value["type"], "latest")
        self.assertEqual(value["value"], "c")

    def test_get_summary_writes_warning_to_output_when_unsupported_method_requested(self):
        data_tools = [
            {"field":"number", "method":"cow"},
            {"field":"number", "method":"moose"},
        ]

        C = DictConnection()
        topic_id = C.add_topic("topic", description="description", fields=["number"], data_tools=data_tools)
        C.add_data(topic_id, {"number": 3})
        summary = C.get_summary(topic_id)
        self.assertEqual(summary["warnings"], [
            'The requested method "cow" is not supported.',
            'The requested method "moose" is not supported.'
        ])

    def test_get_latest_handles_empty_list(self):
        C = DictConnection()
        topic_id = C.add_topic("topic")
        with self.assertRaises(IndexError):
            C.get_latest(topic_id)

    def test_get_latest_returns_latest_data_element_for_topic(self):
        C = DictConnection()
        topic_id = C.add_topic("topic", description="description", fields=["number"])
        C.add_data(topic_id, {"number": 3})
        C.add_data(topic_id, {"number": 2})
        C.add_data(topic_id, {"number": 1})

        latest = C.get_latest(topic_id)
        self.assertEqual(latest["number"], 1)

    def test_last_truthy_falsy_summary_returns_correct_timestamp(self):
        data_tools = [
            {"field":"onoff", "method":"last_truthy"},
            {"field":"onoff", "method":"last_falsy"}
        ]

        C = DictConnection()
        topic_id = C.add_topic("topic", description="description", fields=["onoff"], data_tools=data_tools)
        for i in [False, True, False, True]:
            C.add_data(topic_id, {"onoff": i})

        summary = C.get_summary(topic_id)
        data = C.get_data(topic_id)

        self.assertEqual(summary["statistics"][0]["payload"]["value"], data[3]["timestamp"])
        self.assertEqual(summary["statistics"][1]["payload"]["value"], data[2]["timestamp"])

    def _test_run_data_tools_for_many(self, fn, data_tools):
        topic_ids = []
        C = DictConnection()
        for i in range(3):
            topic_ids.append(
                C.add_topic(
                    "topic_" + str(i),
                    description="description",
                    fields=["number"],
                    data_tools=data_tools
            ))
            C.add_data(topic_ids[-1], {"number": 3})
            C.add_data(topic_ids[-1], {"number": 4})
            C.add_data(topic_ids[-1], {"number": 2})
        if fn == "get_comparison":
            result = C.get_comparison(topic_ids)
        elif fn == "get_overview":
            result = C.get_overview()
        self.assertEqual(result["topic_names"], ["topic_0", "topic_1", "topic_2"])
        self.assertEqual(result["fields"], ["number"])

        return result

    def test_get_comparison_produces_comparison(self):
        data_tools = [{"field":"number", "method":"doughnut", "metadata": dict(asd=123)}]
        result = self._test_run_data_tools_for_many('get_comparison', data_tools)

        self.assertEqual(len(result["statistics"]), 1)
        self.assertEqual(result["statistics"][0]["metadata"]["asd"], 123)

    def test_get_overview_produces_overview(self):
        data_tools = [{"field":"number", "method":"latest"}]
        result = self._test_run_data_tools_for_many('get_overview', data_tools)

        self.assertEqual(len(result["statistics"]), 3)


    def test_overview_and_comparison_include_units(self):
        data_tools = [
            {"field":"number", "method":"latest"},
        ]

        units_d = {"field":"number", "unit":"scalar"}

        C = DictConnection()
        for i in range(3):
            topic_id = C.add_topic(
                "topic_" + str(i),
                description="description",
                fields=["number"],
                data_tools=data_tools,
                units=[units_d]
            )
            C.add_data(topic_id, {"number": i})
        overview = C.get_overview()
        self.assertEqual(overview["topic_names"], ["topic_0", "topic_1", "topic_2"])
        self.assertEqual(overview["fields"], ["number"])

        self.assertEqual(len(overview["statistics"]), 3)
        self.assertEqual(overview["statistics"][0]["payload"]["unit"], "scalar")