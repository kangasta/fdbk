from unittest import TestCase
from unittest.mock import Mock, patch

from fdbk.data_tools import functions

class DBConnectionTest(TestCase):
    def test_summary_funcs_return_none_on_empty_data(self):
        for fn in functions.values():
            self.assertIsNone(fn([], 'field'))
