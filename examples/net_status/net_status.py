from datetime import timedelta

from requests import get
from requests.exceptions import ReadTimeout

class NetStatus(object):
    @staticmethod
    def _validate(target):
        try:
            assert type(target.get('name')) is str
            assert type(target.get('url')) is str
        except AssertionError:
            raise ValueError('Invalid target: ' + str(target))

    def __init__(self, target, timeout=3):
        self._validate(target)

        self._target = target
        self._timeout = timeout

    @property
    def template(self):
        return {
            "name": "netstatus",
            "type_str": "template",
            "description": "Network connection status monitor.",
            "fields": ['elapsed', 'status_code'],
            "units": [{
                'field': 'elapsed',
                'unit': 'ms',
            }],
            "data_tools": [{
                "field": 'status_code',
                "method": "table_item",
                "parameters": {"method": "status", "name": "Status", "parameters": {
                    "method": "latest", "default": "ERROR", "checks": [
                        {"status": "SUCCESS", "operator": "and", "gte": 200, "lt": 300, }
                    ]
                }}
            },{
                "field": 'status_code',
                "method": "table_item",
                "parameters": { "method": "latest", "name": "Status" }
            },{
                "field": 'elapsed',
                "method": "table_item",
                "parameters": { "method": "latest", "name": "Status" }
            },{
                "field": 'elapsed',
                "method": "line",
            }],
        }

    @property
    def topic(self):
        return {
            "name": self._target.get('name'),
            "template": "netstatus",
            "type_str": "topic",
            "metadata": {"url": self._target.get('url')},
        }

    @property
    def data(self):
        data = {}

        try:
            response = get(self._target.get('url'), timeout=self._timeout)
            data['elapsed'] = (response.elapsed / timedelta(microseconds=1)) / 1000.0
            data['status_code'] = response.status_code
        except ReadTimeout:
            data['elapsed'] = self._timeout * 1000.0
            data['status_code'] = None

        return data

if __name__ == '__main__':
    def main():
        parser = get_reporter_argparser()

        parser.add_argument("--target", "-t", action="append", default=[], type=str, nargs=2, metavar=("name","url"), help="Add target to monitor.")
        parser.add_argument("--timeout", default=3, type=float, help="Timeout for network requests.")
        parser.add_argument("--target-file", "-f", type=str, help="Add targets from json file to monitor.")
        args = parser.parse_args()

        targets_cmd = [{'name': name, 'url': url} for name, url in args.target]
        if args.target_file is not None:
            with open(args.target_file) as f:
                targets_file = json.load(f)
        else:
            targets_file = []

        targets = targets_cmd + targets_file
        data_sources = (NetStatus(target, args.timeout) for target in targets)

        db_connection = create_db_connection(args.db_connection, args.db_parameters)

        reporters = (Reporter(data_source, db_connection, verbose=args.verbose) for data_source in data_sources)

        threads = []
        for reporter in reporters:
            threads.append(Thread(target=reporter.start, kwargs=dict(interval=args.interval, num_samples=args.num_samples, stop_on_errors=args.stop_on_errors)))
            threads[-1].start()

        for thread in threads:
            thread.join()


    from argparse import ArgumentParser
    import json
    from threading import Thread

    from fdbk import Reporter
    from fdbk.utils import create_db_connection, get_reporter_argparser

    main()