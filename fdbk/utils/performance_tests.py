from datetime import datetime

from fdbk.reporter import Reporter
from fdbk.utils import TestTopicWeather


class Timer:
    def __init__(self):
        self._started = None
        self._finished = None

    def __enter__(self):
        self._started = datetime.utcnow()
        return self

    def __exit__(self, type_, value, traceback):
        self._finished = datetime.utcnow()
        return False

    @property
    def elapsed(self):
        '''Return elapsed time in milliseconds
        '''
        if not self._finished or not self._started:
            return None

        return (self._finished - self._started).total_seconds() * 1000


def initialize(data_source, db_plugin='dict', db_parameters=None):
    '''Initialize a reporter for performance test
    '''
    if db_parameters is None:
        db_parameters = []

    reporter = Reporter(
        data_source,
        db_plugin=db_plugin,
        db_parameters=db_parameters)

    return reporter


def add_data(reporter, data_source, count=1000):
    '''Add N data-points to DB via reporter from the given data source
    '''
    with Timer() as t:
        for _ in range(count):
            reporter.push(data_source.data)
    return t.elapsed


def run_data_tools(reporter):
    '''Run data tools for topic id stored in the reporter
    '''
    db_connection = reporter.connection
    topic_id = reporter.topic_id

    with Timer() as t:
        db_connection.get_summary(topic_id)

    return t.elapsed


if __name__ == '__main__':
    from ._connection import get_connection_argparser

    parser = get_connection_argparser(default_db_plugin='dict')
    args = parser.parse_args()

    data_source = TestTopicWeather('Weather data performance tests')

    print('*   Run fdbk performance tests')
    print('**  Weather data')

    for count, description in [
        (24 * 2 * 30, '30 minute interval for a month'),
        (24 * 4 * 30, '15 minute interval for a month'),
        (24 * 60 * 30, '1 minute interval for a month'),
        (24 * 60 * 4 * 30, '15 second interval for a month'),
    ]:
        print(f'*** {description} (N = {count})')

        reporter = initialize(
            data_source,
            args.db_connection,
            args.db_parameters)

        add_elapsed = add_data(reporter, data_source, count)
        print(f'Add data:       {add_elapsed:.3f} ms')

        data_tools_elapsed = run_data_tools(reporter)
        print(f'Run data tools: {data_tools_elapsed:.3f} ms')
