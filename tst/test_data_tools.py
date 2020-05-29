from unittest import TestCase
from unittest.mock import Mock, patch

from fdbk.data_tools import functions

def generate_test_numbers(N=10):
    return [dict(number=i) for i in range(N)]

class DataToolsTest(TestCase):
    def test_summary_funcs_return_none_on_empty_data(self):
        for fn in functions.values():
            self.assertIsNone(fn([], 'field'))

    def test_value_functions(self):
        data = generate_test_numbers()

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