import psutil

from threading import Thread, RLock

from requests import get
from requests.exceptions import ReadTimeout

class SysStatus(object):
    def __init__(self, topic_name='System status'):
        self.__topic_name = topic_name

    @property
    def template(self):
        fields = ['CPU_usage', 'memory_usage', 'disk_usage']
        units = (
            list(map(lambda field: {'field': field, 'unit': 'percent'}, fields))
        )

        return {
            "name": "sysstatus",
            "type_str": "template",
            "description": "System status monitor.",
            "fields": fields,
            "units": units,
            "data_tools": list(map(lambda field: {
                "field": field,
                "method":"latest"
            }, fields)) + list(map(lambda field: {
                "field": field,
                "method":"line"
            }, fields))
        }

    @property
    def topic(self):
        return {
            "name": self.__topic_name,
            "template": "sysstatus",
            "type_str": "topic",
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
    from fdbk.utils import get_reporter_argparser

    parser = get_reporter_argparser()
    args = parser.parse_args()

    SYS_STATUS = SysStatus()

    REPORTER = Reporter(SYS_STATUS, db_plugin=args.db_connection, db_parameters=args.db_parameters, verbose=args.verbose)
    REPORTER.start(interval=args.interval, num_samples=args.num_samples)
