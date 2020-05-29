'''Example DB connection implemented with Python dict as the storage
'''

from os.path import expanduser
import json

from fdbk import DBConnection
from fdbk.utils import (
    generate_data_entry,
    generate_data_response,
    generate_topic_dict,
    generate_topic_response,
    generate_topics_list)
from fdbk.utils.messages import *


class DictConnection(DBConnection):
    '''Example DB connection implemented with Python dict as the storage
    '''

    def __init__(self, topics_db_backup=None):
        self._topics_backup = topics_db_backup
        topics = []

        if self._topics_backup:
            try:
                with open(expanduser(self._topics_backup), 'r') as f:
                    topics = json.load(f)['topics']
            except FileNotFoundError:
                pass

        self._dict = {
            "topics": topics
        }

    def add_topic(self, name, **kwargs):
        topic_d = generate_topic_dict(name, add_id=True, **kwargs)

        self._dict["topics"].append(topic_d)
        self._dict[topic_d["id"]] = []

        if self._topics_backup:
            with open(expanduser(self._topics_backup), 'w') as f:
                json.dump({'topics': self._dict["topics"]}, f)

        return topic_d["id"]

    def add_data(self, topic_id, values):
        topic_d = self._get_topic_dict(topic_id)
        fields = topic_d["fields"]

        data = generate_data_entry(topic_id, fields, values)
        self._dict[topic_id].append(data)

    def get_topics(self, type_=None):
        topics = self._dict["topics"]
        if type_:
            topics = [i for i in topics if i.get('type') == type_]

        return generate_topics_list(topics)

    def _get_topic_dict(self, topic_id):
        try:
            return next(
                i for i in self._dict["topics"] if i["id"] == topic_id)
        except StopIteration:
            raise KeyError(topic_not_found(topic_id))

    def get_topic(self, topic_id):
        return generate_topic_response(self._get_topic_dict(topic_id))

    def get_data(self, topic_id, since=None, until=None, limit=None):
        topic_d = self._get_topic_dict(topic_id)
        fields = topic_d["fields"]
        data = self._dict[topic_id]

        if since:
            data = (i for i in data if i.get('timestamp') >= since)
        if until:
            data = (i for i in data if i.get('timestamp') <= until)

        data = list(data)

        if limit:
            data = data[-(limit or 0):]

        return generate_data_response(data, fields)


ConnectionClass = DictConnection
