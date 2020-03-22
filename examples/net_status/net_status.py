from datetime import timedelta

from threading import Thread, RLock

from requests import get
from requests.exceptions import ReadTimeout

class NetStatus(object):
    @staticmethod
    def __validate_targets(targets):
        for target in targets:
            try:
                assert type(target['name']) is str
                assert type(target['url']) is str
            except AssertionError:
                raise ValueError('Invalid target: ' + str(target))

    def __init__(self, targets, topic_name='Network status', timeout=2):
        if type(targets) is not list or len(targets) == 0:
            raise ValueError('No targets given')

        self.__validate_targets(targets)

        self.__targets = targets
        self.__timeout = timeout
        self.__topic_name = topic_name

    @property
    def topic(self):
        target_names = [target['name'] for target in self.__targets]
        fields = (
            list(map(lambda name: name + '_elapsed', target_names)) +
            list(map(lambda name: name + '_status_code', target_names))
        )
        units = (
            list(map(lambda name: {
                'field': name + '_elapsed',
                'unit': 'ms'
            }, target_names))
        )

        return {
            "name": self.__topic_name,
            "type_str": "netstatus",
            "description": "Network connection status monitor.",
            "fields": fields,
            "units": units,
            "summary": list(map(lambda field: {
                "field": field,
                "method":"latest"
            }, (target['name'] + '_elapsed' for target in self.__targets))),
            "visualization": list(map(lambda field: {
                "field": field,
                "method":"line"
            }, (target['name'] + '_elapsed' for target in self.__targets)))
        }

    @property
    def data(self):
        lock = RLock()
        data = {}

        def __run_get(name, url):
            try:
                response = get(url, timeout=self.__timeout)
                with lock:
                    data[name + '_elapsed'] = (response.elapsed / timedelta(microseconds=1)) / 1000.0
                    data[name + '_status_code'] = response.status_code
            except ReadTimeout:
                with lock:
                    data[name + '_elapsed'] = self.__timeout * 1000.0
                    data[name + '_status_code'] = None

        threads = []
        for target in self.__targets:
            threads.append(Thread(target=__run_get, args=[target['name'], target['url']]))
            threads[-1].start()

        for thread in threads:
            thread.join()

        return data

if __name__ == '__main__':
    from argparse import ArgumentParser
    import json

    from fdbk import Reporter

    parser = ArgumentParser()

    parser.add_argument("db_parameters", nargs="+", type=str, help="Parameters for fdbk DB connection.")
    parser.add_argument("--db-connection", type=str, default="ClientConnection", help="fdbk DB connection to use (default=ClientConnection)")
    parser.add_argument("--interval", "-i", type=float, default=360.0, help="Data pushing interval in seconds.")
    parser.add_argument("--num-samples", "-n", type=int, default=60, help="Number of samples to average during the push interval")

    parser.add_argument("--target", "-t", action="append", default=[], type=str, nargs=2, metavar=("name","url"), help="Add target to monitor.")
    parser.add_argument("--target-file", "-f", type=str, help="Add targets from json file to monitor.")
    args = parser.parse_args()

    targets_cmd = [{'name': name, 'url': url} for name,url in args.target]
    if args.target_file is not None:
        with open(args.target_file) as f:
            targets_file = json.load(f)
    else:
        targets_file = []

    NET_STATUS = NetStatus(targets_cmd + targets_file)

    REPORTER = Reporter(NET_STATUS, args.db_connection, args.db_parameters)
    REPORTER.start(interval=args.interval, num_samples=args.num_samples)
