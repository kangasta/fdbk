from datetime import datetime
from random import randrange
from unittest import TestCase
from unittest.mock import Mock, patch

from freezegun import freeze_time

from fdbk import Reporter, DictConnection
from fdbk.reporter import _add, _div, _obj_add, _Data

class TestDataSource:
    def __init__(self, pattern, n):
        self._pattern = pattern
        self._i = 0
        self._n = n

    @property
    def topic(self):
        return {
            "name": "topic",
            "fields": [ "number" ]
        }

    @property
    def data(self):
        i = self._i
        self._i += 1

        if i >= self._n:
            return None

        p = self._pattern
        try:
            num = p[i % len(p)]
        except Exception:
            raise KeyboardInterrupt
        return {
            "number": num
        }

class TestDataSourceWithTemplate:
    @property
    def template(self):
        return {
            "name": "random",
            "description": "Random numbers from randrange(10)",
            "type_str": "template",
            "fields": [ "number" ]
        }

    @property
    def topic(self):
        return {
            "name": "topic",
            "template": "random",
        }

    @property
    def data(self):
        return {
            "number": randrange(10)
        }

class ReporterUtilsTest(TestCase):
    def test_add_and_div_returns_none_on_error(self):
        self.assertIsNone(_add(1, None))
        self.assertIsNone(_div(1, 0))

    def test_obj_add_raises_value_error_on_non_matching_dicts(self):
        with self.assertRaises(ValueError):
            _obj_add(dict(a=1), dict(b=2))

    def test_data_averaged_return_none_on_empty_data(self):
        self.assertIsNone(_Data().averaged)

    def test_data_has_age_property(self):
        with freeze_time(datetime(2020,1,1,1,30)):
            data = _Data()
        with freeze_time(datetime(2020,1,1,1,31)):
            self.assertEqual(data.age, 60)

    def test_data_add_raises_value_error_on_non_matching_data(self):
        data = _Data()
        data.add(dict(a=1))

        with self.assertRaises(ValueError):
            data.add(dict(b=2))

    def test_data_has_reset_method(self):
        data = _Data()
        data.add(dict(a=1))
        self.assertEqual(data.averaged, dict(a=1))

        data.reset()
        self.assertIsNone(data.averaged)

        data.add(dict(b=2))
        self.assertEqual(data.averaged, dict(b=2))

class ReporterTest(TestCase):
    def test_raises_error_with_invalid_db_connection(self):
        DS = TestDataSource([0], 1)
        with self.assertRaises(RuntimeError):
            R = Reporter(DS, db_plugin='NoConnection')

    def test_creates_topic_on_init(self):
        DS = TestDataSource([1,2,3], 3)
        R = Reporter(DS, db_plugin='DictConnection')
        C = R.connection
        self.assertEqual(C.get_topic(R.topic_id)["name"], "topic")
        self.assertEqual(C.get_topic(R.topic_id)["fields"], ["number"])

    def test_creates_template_on_init(self):
        DS = TestDataSourceWithTemplate()
        R = Reporter(DS, db_plugin='DictConnection')
        C = R.connection
        self.assertEqual(len(C.get_topics()), 2)
        self.assertEqual(C.get_topics()[0]["type"], "template")

        R = Reporter(DS, db_connection=C)
        self.assertEqual(len(C.get_topics()), 3)

    def test_can_use_existing_connection(self):
        DS = TestDataSource([1,2,3], 3)
        C = DictConnection()
        R = Reporter(DS, db_connection=C)

        self.assertEqual(C.get_topic(R.topic_id)["name"], "topic")
        self.assertEqual(C.get_topic(R.topic_id)["fields"], ["number"])

    def test_reports_data_until_None(self):
        DS = TestDataSource([1,2,3], 3)
        R = Reporter(DS, db_plugin='DictConnection')
        R.start(interval=0, num_samples=1)

        C = R.connection
        self.assertEqual(3, len(C.get_data(R.topic_id)))

    def test_start_method_catches_ctrl_c(self):
        DS = TestDataSource([], 5)
        R = Reporter(DS, db_plugin='DictConnection')
        R.start(interval=0, num_samples=1)

    def test_start_supports_non_numeric_values(self):
        DS = TestDataSource(['qwe', 'asd', 'zxc'], 3)
        R = Reporter(DS, db_plugin='DictConnection')
        R.start(interval=0, num_samples=1)

        C = R.connection
        self.assertEqual(3, len(C.get_data(R.topic_id)))
        self.assertEqual('asd', C.get_data(R.topic_id)[1]['number'])

    def test_provides_averaging_over_push_interval(self):
        DS = TestDataSource([0, 2, 4, 6, 8, 10], 6)
        R = Reporter(DS, db_plugin='DictConnection')
        R.start(interval=0, num_samples=6)

        C = R.connection
        data = C.get_data(R.topic_id)
        self.assertEqual(1, len(data))
        self.assertAlmostEqual(5, data[0]["number"])

    def test_averaging_ignores_samples_with_none(self):
        # TODO check for warning
        DS = TestDataSource([0, 2, None, 6, None, 10], 6)
        R = Reporter(DS, db_plugin='DictConnection')
        R.start(interval=0, num_samples=6)

        C = R.connection
        data = C.get_data(R.topic_id)
        self.assertEqual(1, len(data))
        self.assertAlmostEqual(4.5, data[0]["number"])

    def test_averaging_wont_push_if_no_valid_samples(self):
        DS = TestDataSource([None, None, None], 3)
        R = Reporter(DS, db_plugin='DictConnection')
        R.start(interval=0, num_samples=6)

        C = R.connection
        data = C.get_data(R.topic_id)
        self.assertEqual(0, len(data))

    @patch.object(DictConnection, 'add_data', side_effect=RuntimeError("Test error"))
    def test_averaging_wont_pass_through_exception_on_failed_push(self, mock):
        DS = TestDataSource([1,2,3], 3)
        R = Reporter(DS, db_plugin='DictConnection')
        R.start(interval=0, num_samples=1)

        C = R.connection
        data = C.get_data(R.topic_id)
        self.assertEqual(3, len(mock.mock_calls))
        self.assertEqual(0, len(data))

        R.push({'number': 3})

    @patch.object(DictConnection, 'add_data')
    def test_push_is_skipped_on_empty_data(self, mock):
        DS = TestDataSource([1,2,3], 3)
        R = Reporter(DS, db_plugin='DictConnection')
        R.push()

        mock.assert_not_called()

    def test_provides_push_method(self):
        DS = TestDataSource([], 0)
        R = Reporter(DS, db_plugin='DictConnection')
        for i in range(3):
            R.push({'number': i})

        C = R.connection
        self.assertEqual(3, len(C.get_data(R.topic_id)))
        self.assertEqual(0, C.get_data(R.topic_id)[0]['number'])

    def test_allows_custom_print_fn(self):
        print_mock = Mock()

        DS = TestDataSource([], 0)
        R = Reporter(DS, db_plugin='DictConnection', verbose=False, print_fn=print_mock)
        R._print('asd')
        print_mock.assert_not_called()

        R = Reporter(DS, db_plugin='DictConnection', verbose=True, print_fn=print_mock)
        R._print('asd')
        print_mock.assert_called()

    @patch.object(DictConnection, 'add_data')
    def test_push_automatically_on_report_for_num_samples(self, add_mock):
        DS = TestDataSource([], 0)
        R = Reporter(DS, db_plugin='DictConnection', verbose=False, num_samples=2)

        for i in range(5):
            R.report(dict(a=1))
            self.assertEqual(i, len(add_mock.mock_calls))

            R.report(dict(a=1))
            self.assertEqual(i+1, len(add_mock.mock_calls))

    @patch.object(DictConnection, 'add_data')
    def test_push_automatically_on_report_for_interval(self, add_mock):
        DS = TestDataSource([], 0)
        R = Reporter(DS, db_plugin='DictConnection', verbose=False, interval=120)

        for i in range(1,10):
            with freeze_time(datetime(2020,1,1,1,i)):
                R.report(dict(a=i))
                if not i % 3:
                    add_mock.assert_called()
                    self.assertIsNone(R._data)
                    add_mock.reset_mock()
                else:
                    add_mock.assert_not_called()
                    self.assertIsNotNone(R._data)

    def test_topic_creation_fails_without_data_source(self):
        with self.assertRaises(ValueError):
            R = Reporter(None, db_plugin='DictConnection')

    def test_data_collection_fails_without_data_source(self):
        R = Reporter(None, db_plugin='DictConnection', topic_id='123')

        with self.assertRaises(ValueError):
            R.start()

    def test_data_can_be_pushed_to_existing_topic(self):
        R = Reporter(None, db_plugin='DictConnection', topic_id='TBD')
        topic_id = R.connection.add_topic(**TestDataSource([],0).topic)
        R._topic_id = topic_id

        R.push(dict(a=1))
