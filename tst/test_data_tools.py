from os import path
from unittest import TestCase
from unittest.mock import Mock, patch
import yaml

from fdbk.data_tools import aggregate, functions, run_data_tools, post_process
from fdbk.utils.messages import method_not_supported, no_data
from fdbk.validate import validate_statistics_array

def _test_timestamp(i, timestamps=None):
    if timestamps:
        return timestamps[i]
    return f'2020-08-23T00:{i // 60:02}:{i % 60:02}Z'

def generate_test_data(N=10, timestamps=None):
    return [dict(number=i, number2=i*2, letter=chr(ord('A') + i), timestamp=_test_timestamp(i, timestamps)) for i in range(N)]

STATUS_TOPIC = dict(name='Test status', fields=["number", "number2", "letter"], units=[dict(field="number", unit="scalar")], data_tools=[])
AGGREGATE_ALWAYS_TOPIC = dict(
    name="Aggregate test",
    fields=["number", "number2", "letter"],
    data_tools=[{"field":"number", "method":"line"},])
AGGREGATE_ALWAYS_DATA = generate_test_data(4, [
    '2020-09-12T00:00:00Z',
    '2020-09-12T00:00:01Z',
    '2020-09-12T00:00:02Z',
    '2020-09-13T00:00:00Z',])

class DataToolsTest(TestCase):
    def test_summary_funcs_return_none_on_empty_data(self):
        for fn in functions.values():
            self.assertIsNone(fn([], 'field'))

    def test_run_data_tools_empty_data(self):
        topic_d = dict(id='test_id', name='Test name')
        data = []

        def _check_results(results, warnings, topic_d=None):
            self.assertEqual(result, [])
            self.assertEqual(
                warnings[0],
                no_data(topic_d))

        result, warnings = aggregate(data, 3)
        _check_results(result, warnings)

        result, warnings = run_data_tools(topic_d, data)
        _check_results(result, warnings, topic_d)


    def test_value_functions(self):
        data = generate_test_data()

        tests = [
            ('average', 4.5,),
            ('mean', 4.5,),
            ('median', 4.5,),
            ('min', 0,),
            ('max', 9,),
            ('sum', 45,),
        ]

        for type_, value in tests:
            result = functions.get(type_)(data, 'number')

            self.assertEqual(result.get('payload').get('type'), type_)
            self.assertEqual(result.get('payload').get('value'), value)

    def test_collection_functions_unit(self):
        topic_d = STATUS_TOPIC
        data = generate_test_data()

        topic_d['data_tools'] = [
            dict(field='number', method="average"),
            dict(field='number', method='list_item', parameters=dict(
                name="test_list", method="average")),
            dict(field='number', method='table_item', parameters=dict(
                name="test_table", method="average")),
        ]

        results, warnings = run_data_tools(topic_d, data)
        self.assertEqual(len(warnings), 0)

        results, warnings = post_process(results)
        self.assertEqual(len(warnings), 0)
        validate_statistics_array(results)

        self.assertEqual(len(results), 3)

        value = next(i for i in results if i["type"] == "value")
        self.assertEqual(
            value["payload"]["unit"], "scalar")
        list_ = next(i for i in results if i["type"] == "list")
        self.assertEqual(
            list_["payload"]["data"][0]["payload"]["unit"], "scalar")
        table = next(i for i in results if i["type"] == "table")
        self.assertEqual(
            table["payload"]["data"][0]["data"][0]["payload"]["unit"], "scalar")


    def test_status_functions(self):
        topic_d = STATUS_TOPIC
        data = generate_test_data()

        self.assertIsNone(functions.get('status')(data, 'number'))

        with open(path.join(path.dirname(__file__), 'status_functions_testdata.yaml')) as f:
            tests = yaml.safe_load(f)['tests']

        for kwargs, status in tests:
            result = functions.get('status')(data, 'number', **kwargs)
            self.assertEqual(result.get('payload').get('status'), status, msg=str(kwargs))

            topic_d['data_tools'] = [dict(field='number', method='status', **kwargs)]
            results, warnings = run_data_tools(topic_d, data)
            validate_statistics_array(results)
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].get('payload').get('status'), status, msg=str(kwargs))
            self.assertEqual(len(warnings), 0)

    def test_status_functions_warnings(self):
        topic_d = STATUS_TOPIC
        data = generate_test_data()

        with open(path.join(path.dirname(__file__), 'status_functions_testdata.yaml')) as f:
            tests = yaml.safe_load(f)['warnings_tests']

        for kwargs, text in tests:
            topic_d['data_tools'] = [dict(field='number', method='status', **kwargs)]
            results, warnings = run_data_tools(topic_d, data)

            self.assertEqual(len(warnings), 1)
            self.assertIn(text, warnings[0])

    def test_status_functions_in_collection(self):
        topic_d = STATUS_TOPIC
        data = generate_test_data()

        parameters = dict(method="status", name="Test table", parameters={
            "method": "latest",
            "default": "ERROR",
            "checks": [
                {"status": "SUCCESS", "operator": "and", "gte": 9, }
            ]
        })
        topic_d['data_tools'] = [dict(field='number', method='table_item', parameters=parameters)]

        results, warnings = run_data_tools(topic_d, data)
        self.assertEqual(len(warnings), 0)

        results, warnings = post_process(results)
        self.assertEqual(len(warnings), 0)

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0]['payload']['data'][0]['data'][0]['payload']['status'],
            'SUCCESS')

    def test_invalid_functions_in_collection(self):
        topic_d = STATUS_TOPIC
        data = generate_test_data()

        parameters = dict(method="bear", name="Test invalid")
        topic_d['data_tools'] = [dict(field='number', method='table_item', parameters=parameters)]

        results, warnings = run_data_tools(topic_d, data)
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0], method_not_supported('bear'))
        self.assertEqual(len(results), 0)

    def test_aggregate(self):
        data = generate_test_data(51)
        aggregated, warnings = aggregate(data, 5)

        for i in range(1,5):
            self.assertEqual(aggregated[i].get('timestamp'), _test_timestamp(i*10))
            num = 5.5 + 10 * i
            self.assertEqual(aggregated[i].get('number'), num)
            self.assertEqual(aggregated[i].get('number2'), num * 2)

    def test_aggregate_min(self):
        data = generate_test_data(51)
        aggregated, warnings = aggregate(data, 5, 'min')

        for i in range(1,5):
            self.assertEqual(aggregated[i].get('timestamp'), _test_timestamp(i*10))
            num = 1 + 10 * i
            self.assertEqual(aggregated[i].get('number'), num)
            self.assertEqual(aggregated[i].get('number2'), num * 2)

    def test_aggregate_empty_window(self):
        data = generate_test_data(5)
        aggregated, warnings = aggregate(data, 10, 'max', aggregate_always=True)

        for i in range(1, 5):
            self.assertNotEqual(aggregated[i].get('timestamp'), _test_timestamp(i))
            self.assertEqual(aggregated[i].get('number'), i)
            self.assertEqual(aggregated[i].get('number2'), i * 2)

    def test_aggregate_unknown_data_tool(self):
        data = generate_test_data(15)
        aggregated, warnings = aggregate(data, 10, 'horse')

        self.assertEqual(aggregated, [])
        self.assertEqual(warnings, [method_not_supported('horse')])

    def test_aggregate_always(self):
        data = AGGREGATE_ALWAYS_DATA
        aggregated, warnings = aggregate(data, 5)

        self.assertEqual(aggregated, data)
        self.assertEqual(warnings, [])

        aggregated, warnings = aggregate(data, 5, aggregate_always=True)

        self.assertEqual(len(aggregated), 2)
        self.assertEqual(aggregated[0]["number"], 1)
        self.assertEqual(aggregated[1]["number"], 3)
        self.assertEqual(warnings, [])

    def test_warning_functions(self):
        topic_d = STATUS_TOPIC
        data = generate_test_data()

        for check, expected in [
            (dict(operator='and', gte=4, lte=6), ["Test warning"]),
            (dict(operator='and', gte=6, lte=4), []),
        ]:
            parameters=dict(
                method="average",
                message="Test warning",
                check=check,
            )

            topic_d['data_tools'] = [
                dict(field='number', method="warning", parameters=parameters),
            ]

            results, warnings = run_data_tools(topic_d, data)

            self.assertEqual(len(results), 0)
            self.assertEqual(len(warnings), len(expected))

            if expected:
                self.assertEqual(warnings[0], "Test warning")
