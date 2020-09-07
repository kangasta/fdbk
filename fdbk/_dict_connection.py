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
    generate_topics_list,
    timestamp_as_str)
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

    def _topic_i(self, topic_id):
        return next(
            i for i, data in enumerate(
                self._dict["topics"]) if data["id"] == topic_id)

    def add_topic(self, name, overwrite=False, **kwargs):
        topic_d = generate_topic_dict(name, add_id=True, **kwargs)
        self.validate_template(topic_d)

        try:
            i = self._topic_i(topic_d["id"])
            if not overwrite:
                raise KeyError(duplicate_topic_id(topic_d["id"]))
            self._dict["topics"][i] = topic_d
        except StopIteration:
            self._dict["topics"].append(topic_d)
            self._dict[topic_d["id"]] = []

        if self._topics_backup:
            with open(expanduser(self._topics_backup), 'w') as f:
                json.dump({'topics': self._dict["topics"]}, f)

        return topic_d["id"]

    def _timestamp_i(self, topic_id, timestamp):
        return next(
            i for i, data in enumerate(
                self._dict[topic_id]) if data["timestamp"] == timestamp)

    def add_data(self, topic_id, values, overwrite=False):
        topic_d = self.get_topic(topic_id)
        if topic_d.get('type') == 'template':
            raise AssertionError('Cannot add data to template topic.')
        fields = topic_d["fields"]

        data = generate_data_entry(topic_id, fields, values)

        try:
            i = self._timestamp_i(topic_id, data['timestamp'])
            if not overwrite:
                raise AssertionError(
                    duplicate_timestamp(topic_d, data['timestamp']))
            self._dict[topic_id][i] = data
        except StopIteration:
            self._dict[topic_id].append(data)

        return timestamp_as_str(data['timestamp'])

    def get_topics_without_templates(self, type_=None, template=None):
        topics = self._dict["topics"]
        if type_:
            topics = [i for i in topics if i.get('type') == type_]
        if template:
            topics = [i for i in topics if i.get('template') == template]

        return generate_topics_list(topics)

    def _get_topic_dict(self, topic_id):
        try:
            return next(
                i for i in self._dict["topics"] if i["id"] == topic_id)
        except StopIteration:
            raise KeyError(topic_not_found(topic_id))

    def get_topic_without_templates(self, topic_id):
        return generate_topic_response(self._get_topic_dict(topic_id))

    def get_data(self, topic_id, since=None, until=None, limit=None):
        topic_d = self.get_topic(topic_id)
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
