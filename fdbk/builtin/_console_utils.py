from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import os
import re


def command_as_str(command):
    return ' '.join(i if not re.search(r'\s', i)
                    else f"'{i}'" for i in command)


def _current_timestamp():
    return f'{datetime.utcnow().isoformat()}Z'


def _read_stream(stream_name, stream_fd, encoding):
    f = os.fdopen(stream_fd, encoding=encoding, errors='backslashreplace')
    data = []

    for line in iter(f.readline, ''):
        data.append(dict(
            stream=stream_name,
            timestamp=_current_timestamp(),
            text=line.rstrip('\n'))),

    f.close()
    return data


class JsonStreams:
    def __init__(self):
        self._writes = []
        self._futures = []
        self._pool = ThreadPoolExecutor(max_workers=3)
        self._data = []

    def __enter__(self):
        stdout = self.create('stdout')
        stderr = self.create('stderr')

        return (stdout, stderr, self,)

    def __exit__(self, type_, value, traceback):
        self.close()

    def push(self, stream_name=None, timestamp=None, text=None):
        if not (stream_name and text):
            raise ValueError(
                'Cannot push data without both stream_name and text.')

        if not timestamp:
            timestamp = _current_timestamp()

        self._data.append(dict(
            stream=stream_name,
            timestamp=timestamp,
            text=text,
        ))

    def create(self, stream_name, encoding='utf-8'):
        read_fd, write_fd = os.pipe()
        self._writes.append(write_fd)
        self._futures.append(
            self._pool.submit(
                _read_stream,
                stream_name,
                read_fd,
                encoding
            ))
        return write_fd

    def close(self):
        for f in self._writes:
            os.close(f)

    def read(self, wait=False):
        data = []
        data.extend(self._data)

        for future in self._futures:
            if not wait and not future.done():
                return None

            data.extend(future.result())

        data.sort(key=lambda i: i.get('timestamp'))
        return data

    @property
    def data(self):
        return self.read()
