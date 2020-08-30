from unittest import TestCase
from unittest.mock import Mock, patch

from fdbk.data_tools import aggregate, functions, run_data_tools
from fdbk.utils.messages import method_not_supported, no_data

def _test_timestamp(i):
    return f'2020-08-23T00:{i // 60:02}:{i % 60:02}Z'

def generate_test_data(N=10):
    return [dict(number=i, number2=i*2, letter=chr(ord('A') + i), timestamp=_test_timestamp(i)) for i in range(N)]

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
        aggregated, warnings = aggregate(data, 10, 'max')

        for i in range(1, 5):
            self.assertNotEqual(aggregated[i].get('timestamp'), _test_timestamp(i))
            self.assertEqual(aggregated[i].get('number'), i)
            self.assertEqual(aggregated[i].get('number2'), i * 2)

    def test_aggregate_unknown_data_tool(self):
        data = generate_test_data(5)
        aggregated, warnings = aggregate(data, 10, 'horse')

        self.assertEqual(aggregated, [])
        self.assertEqual(warnings, [method_not_supported('horse')])
