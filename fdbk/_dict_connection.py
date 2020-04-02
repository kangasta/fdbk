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
    def __init__(self, topics_db_backup=None):
        self.__topics_backup = topics_db_backup
        topics = []

        if self.__topics_backup:
            try:
                with open(expanduser(self.__topics_backup), 'r') as f:
                    topics = json.load(f)['topics']
            except FileNotFoundError:
                pass

        self.__dict = {
            "topics": topics
        }

    def add_topic(self, name, **kwargs):
        topic_d = generate_topic_dict(name, add_id=True, **kwargs)

        self.__dict["topics"].append(topic_d)
        self.__dict[topic_d["id"]] = []

        if self.__topics_backup:
            with open(expanduser(self.__topics_backup), 'w') as f:
                json.dump({'topics': self.__dict["topics"]}, f)

        return topic_d["id"]

    def add_data(self, topic_id, values):
        try:
            topic_d = next(
                i for i in self.__dict["topics"] if i["id"] == topic_id)
        except StopIteration:
            raise KeyError(topic_not_found(topic_id))
        fields = topic_d["fields"]

        data = generate_data_entry(topic_id, fields, values)
        self.__dict[topic_id].append(data)

    def get_topics(self, type_=None):
        topics = self.__dict["topics"]
        if type_:
            topics = [i for i in topics if i.get('type') == type_]

        return generate_topics_list(topics)

    def get_topic(self, topic_id):
        try:
            topic = next(
                i for i in self.__dict["topics"] if i["id"] == topic_id)
        except StopIteration:
            raise KeyError(topic_not_found(topic_id))

        return generate_topic_response(topic)

    def get_data(self, topic_id, since=None, until=None, limit=None):
        try:
            topic_d = next(
                i for i in self.__dict["topics"] if i["id"] == topic_id)
        except StopIteration:
            raise KeyError(topic_not_found(topic_id))
        fields = topic_d["fields"]
        data = self.__dict[topic_id]

        if since:
            data = (i for i in data if i.get('timestamp') >= since)
        if until:
            data = (i for i in data if i.get('timestamp') <= until)

        data = list(data)

        if limit:
            data = data[-(limit or 0):]

        return generate_data_response(data, fields)


ConnectionClass = DictConnection
