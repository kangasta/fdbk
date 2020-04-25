'''Reporter for pushing data from a data source to fdbk
'''

import json
from datetime import datetime
from functools import reduce
from time import sleep

from fdbk import utils


def _add(a, b):
    try:
        return a + b
    except BaseException:
        return None


def _div(a, div):
    try:
        return a / div
    except BaseException:
        return None


def _obj_div(obj, div):
    a = {}
    for key in obj:
        a[key] = _div(obj.get(key), div)

    return a


def _obj_add(a, b):
    if a.keys() != b.keys():
        raise ValueError('Object keys do not match')

    c = {}
    for key in a:
        c[key] = _add(a.get(key), b.get(key))

    return c


class _Data:
    '''Class for storing and averaging Reporter data
    '''

    def __init__(self):
        self._start = datetime.now()
        self._data = []

    def __len__(self):
        return len(self._data)

    @property
    def averaged(self):
        '''Get averaged data or None if no data available

        Returns:
            Object with its values averaged or None if no data available
        '''
        if not self._data:
            return None

        if self.__len__() == 1:
            return self._data[0]

        return _obj_div(reduce(_obj_add, self._data), self.__len__())

    @property
    def age(self):
        '''Get age of the current instance

        Returns:
            Age of the current instance in seconds
        '''
        return (datetime.now() - self._start).total_seconds()

    def add(self, data):
        '''Add data after validating that it matches previous entries

        Args:
            data: Data object to add

        Raises:
            ValueError: Keys of the new object do not match earlier objects
        '''
        if self._data and self._data[0].keys() != data.keys():
            raise ValueError('Object keys do not match')

        self._data.append(data)

    def reset(self):
        '''Clear all data and reset start time
        '''
        self.__init__()


class Reporter:
    '''Class for handling adding new data to fdbk

    Args:
        data_source: Data source to get topic details and new data.
            Is only used with start method.
            Must be set if topic_id not provided.
        db_connection: DB connection to use.
        db_parameters: Parameters for db_connection.
            See connection documentation for details.
        topic_id: ID of topic to push data to.
            Must be set if data_source not provided.
        verbose: Set to falsy to disable usage of print_fn
        interval: Time to average before pushing to DB.
            This parameter only has effect when using push method.
        num_samples: Number of samples to average before pushing to DB.
            This parameter only has effect when using push method.
        print_fn: Function to use printing, print by default
    '''

    def __init__(
            self,
            data_source=None,
            db_connection='',
            db_parameters=None,
            topic_id=None,
            verbose=False,
            interval=None,
            num_samples=None,
            print_fn=print):
        db_parameters = db_parameters if db_parameters is not None else []

        self._data = None
        self._data_source = data_source
        self._topic_id = topic_id

        self._interval = interval
        self._num_samples = num_samples

        self._verbose = verbose
        self._print_fn = print_fn

        self._create_client(db_connection, db_parameters)
        if self._topic_id is None:
            self._create_topic()

    def _create_client(self, db_connection, db_parameters):
        self._client = utils.create_db_connection(
            db_connection, db_parameters)
        self._print(f"Created fdbk DB connection of type "
                    f"'{db_connection}' with parameters {str(db_parameters)}")

    def _create_topic(self):
        if not self._data_source:
            raise ValueError('Cannot create new topic without data source')

        topic_d = self._data_source.topic

        self._print(f"Creating topic '{topic_d['name']}' to fdbk")

        self._topic_id = self._client.add_topic(**topic_d)

    def _print(self, *args, **kwargs):
        if self._verbose:
            self._print_fn(*args, **kwargs)

    @property
    def connection(self):
        '''Get current DB connection instance

        Returns:
            DB connection instance
        '''
        return self._client

    @property
    def data(self):
        '''Get current data

        Returns:
            Current _Data instance
        '''
        if self._data is None:
            self._data = _Data()
        return self._data

    @property
    def topic_id(self):
        '''Get target topic ID

        Returns:
            Target topic ID
        '''
        return self._topic_id

    def push(self, data=None):
        '''Push data to fdbk and reset averaging

        Args:
            data: Data to push, or falsy value to use internal data
        '''
        _data = data if data else self.data.averaged

        if not _data:
            self._print("Push skipped: No valid data to push.")
            return

        try:
            self._client.add_data(self._topic_id, _data)
        except Exception as e:
            self._print(f"Push failed: {str(e)}")
        else:
            self._print(
                f"Push:\n{json.dumps(_data, indent=2, sort_keys=True)}")
        finally:
            if not data:
                self._data = None

    def report(self, data, auto_push=True):
        '''Report data to instances internal storage

        Args:
            data: Data to report
            auto_push: Set to falsy value to disable automatic push when
                interval or num_samples trigger of the instance is reached.

        Raises:
            ValueError: Keys of the new object do not match earlier objects
        '''
        self.data.add(data)

        if not auto_push:
            return

        age_trigger = self._interval and self.data.age >= self._interval
        num_trigger = self._num_samples and len(self.data) >= self._num_samples
        if age_trigger or num_trigger:
            self.push()

    def _collect_data(self, interval, num_samples):
        for _ in range(num_samples):
            sample = self._data_source.data
            if sample is None:
                raise StopIteration()
            if None not in sample.values():
                self.report(sample, auto_push=False)

            if num_samples > 1:
                sleep(float(interval) / num_samples)

    def start(self, interval=360, num_samples=60):
        '''Start pushing data polled from data_source to fdbk

        Args:
            interval: Time to average before pushing to DB.
            num_samples: Number of samples to collect for averaging during the
                interval.

        Raises:
            ValueError: DataSource is not defined.
        '''
        if not self._data_source:
            raise ValueError('Cannot collect data without data source')

        try:
            while True:
                try:
                    self._collect_data(interval, num_samples)
                except StopIteration:
                    return

                self.push()

                if num_samples == 1:
                    sleep(interval)
        except KeyboardInterrupt:
            return
