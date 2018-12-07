from datetime import datetime
from unittest import TestCase
from mongomock import MongoClient as MongoMock

try:
	from unittest.mock import Mock, patch
except ImportError:
	from mock import Mock, patch

from fdbk import MongoConnection

from common_tests import tests

class MongoConnectionTest(TestCase):
	@patch("fdbk.MongoConnection._MongoConnection__get_db", return_value=MongoMock()["db"])
	def test_run_common_tests(self, _):
		for test in tests:
			C = MongoConnection("url")
			test(self, C)
