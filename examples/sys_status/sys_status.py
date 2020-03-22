import psutil

from threading import Thread, RLock

from requests import get
from requests.exceptions import ReadTimeout

class SysStatus(object):
    def __init__(self, topic_name='System status'):
        self.__topic_name = topic_name

    @property
    def topic(self):
        fields = ['CPU_usage', 'memory_usage', 'disk_usage']
        units = (
            list(map(lambda field: {'field': field, 'unit': 'percent'}, fields))
        )

        return {
            "name": self.__topic_name,
            "type_str": "sysstatus",
            "description": "System status monitor.",
            "fields": fields,
            "units": units,
            "summary": list(map(lambda field: {
                "field": field,
                "method":"latest"
            }, fields)),
            "visualization": list(map(lambda field: {
                "field": field,
                "method":"line"
            }, fields))
        }

    @property
    def data(self):
        data = {
            'CPU_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent
        }

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
    args = parser.parse_args()

    SYS_STATUS = SysStatus()

    REPORTER = Reporter(SYS_STATUS, args.db_connection, args.db_parameters)
    REPORTER.start(interval=args.interval, num_samples=args.num_samples)
