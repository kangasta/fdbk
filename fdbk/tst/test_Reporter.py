from unittest import TestCase

try:
	from unittest.mock import Mock, patch
except ImportError:
	from mock import Mock, patch

from fdbk import Reporter

class TestDataSource(object):
	def __init__(self, pattern, n):
		self.__pattern = pattern
		self.__i = 0
		self.__n = n

	@property
	def topic(self):
		return {
			"name": "topic",
			"fields": [ "number" ]
		}

	@property
	def data(self):
		i = self.__i
		self.__i += 1

		if i >= self.__n:
			return None

		p = self.__pattern
		try:
			num = p[i % len(p)]
		except Exception:
			raise KeyboardInterrupt
		return {
			"number": num
		}

class ReporterTest(TestCase):
	def test_raises_error_with_invalid_db_connection(self):
		DS = TestDataSource([0], 1)
		with self.assertRaises(RuntimeError):
			R = Reporter(DS, 'NoConnection')

	def test_creates_topic_on_init(self):
		DS = TestDataSource([1,2,3], 3)
		R = Reporter(DS, 'DictConnection')
		C = R.connection
		self.assertEqual(C.getTopic(R.topic_id)["name"], "topic")
		self.assertEqual(C.getTopic(R.topic_id)["fields"], ["number"])

	def test_reports_data_until_None(self):
		DS = TestDataSource([1,2,3], 3)
		R = Reporter(DS, 'DictConnection', interval=0, num_samples=1)
		R.start()

		C = R.connection
		self.assertEqual(3, len(C.getData(R.topic_id)))

	def test_start_method_catches_ctrl_c(self):
		DS = TestDataSource([], 5)
		R = Reporter(DS, 'DictConnection', interval=0, num_samples=1)
		R.start()

	def test_provides_averaging_over_push_interval(self):
		DS = TestDataSource([0, 2, 4, 6, 8, 10], 6)
		R = Reporter(DS, 'DictConnection', interval=0, num_samples=6)
		R.start()

		C = R.connection
		data = C.getData(R.topic_id)
		self.assertEqual(1, len(data))
		self.assertAlmostEqual(5, data[0]["number"])