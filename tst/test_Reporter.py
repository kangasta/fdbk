from unittest import TestCase
from unittest.mock import Mock, patch

from fdbk import Reporter, DictConnection

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
        self.assertEqual(C.get_topic(R.topic_id)["name"], "topic")
        self.assertEqual(C.get_topic(R.topic_id)["fields"], ["number"])

    def test_reports_data_until_None(self):
        DS = TestDataSource([1,2,3], 3)
        R = Reporter(DS, 'DictConnection')
        R.start(interval=0, num_samples=1)

        C = R.connection
        self.assertEqual(3, len(C.get_data(R.topic_id)))

    def test_start_method_catches_ctrl_c(self):
        DS = TestDataSource([], 5)
        R = Reporter(DS, 'DictConnection')
        R.start(interval=0, num_samples=1)

    def test_start_supports_non_numeric_values(self):
        DS = TestDataSource(['qwe', 'asd', 'zxc'], 3)
        R = Reporter(DS, 'DictConnection')
        R.start(interval=0, num_samples=1)

        C = R.connection
        self.assertEqual(3, len(C.get_data(R.topic_id)))
        self.assertEqual('asd', C.get_data(R.topic_id)[1]['number'])

    def test_provides_averaging_over_push_interval(self):
        DS = TestDataSource([0, 2, 4, 6, 8, 10], 6)
        R = Reporter(DS, 'DictConnection')
        R.start(interval=0, num_samples=6)

        C = R.connection
        data = C.get_data(R.topic_id)
        self.assertEqual(1, len(data))
        self.assertAlmostEqual(5, data[0]["number"])

    def test_averaging_ignores_samples_with_none(self):
        # TODO check for warning
        DS = TestDataSource([0, 2, None, 6, None, 10], 6)
        R = Reporter(DS, 'DictConnection')
        R.start(interval=0, num_samples=6)

        C = R.connection
        data = C.get_data(R.topic_id)
        self.assertEqual(1, len(data))
        self.assertAlmostEqual(4.5, data[0]["number"])

    def test_averaging_wont_push_if_no_valid_samples(self):
        DS = TestDataSource([None, None, None], 3)
        R = Reporter(DS, 'DictConnection')
        R.start(interval=0, num_samples=6)

        C = R.connection
        data = C.get_data(R.topic_id)
        self.assertEqual(0, len(data))

    @patch.object(DictConnection, 'add_data', side_effect=RuntimeError("Test error"))
    def test_averaging_wont_pass_through_exception_on_failed_push(self, mock):
        DS = TestDataSource([1,2,3], 3)
        R = Reporter(DS, 'DictConnection')
        R.start(interval=0, num_samples=1)

        C = R.connection
        data = C.get_data(R.topic_id)
        self.assertEqual(3, len(mock.mock_calls))
        self.assertEqual(0, len(data))

        with self.assertRaises(RuntimeError):
            R.push({'number': 3})

    def test_provides_push_method(self):
        DS = TestDataSource([], 0)
        R = Reporter(DS, 'DictConnection')
        for i in range(3):
            R.push({'number': i})

        C = R.connection
        self.assertEqual(3, len(C.get_data(R.topic_id)))
        self.assertEqual(0, C.get_data(R.topic_id)[0]['number'])
