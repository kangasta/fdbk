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
