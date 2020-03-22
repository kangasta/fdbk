from os.path import expanduser
import json

from fdbk import DBConnection

class DictConnection(DBConnection):
    def __init__(self, topics_db_backup=None):
        self.__topics_backup = topics_db_backup
        topics = []

        if self.__topics_backup:
            try:
                with open(expanduser(self.__topics_backup), 'r') as f:
                    topics = json.load(f)['topics']
            except Exception: # This will be IOError on Python 2 and FileNotFoundError on Python 3
                pass

        self.__dict = {
            "topics": topics
        }

    def add_topic(self, name, **kwargs):
        topic_d = DBConnection.generate_topic_dict(name, add_id=True, **kwargs)

        self.__dict["topics"].append(topic_d)
        self.__dict[topic_d["id"]] = []

        if self.__topics_backup:
            with open(expanduser(self.__topics_backup), 'w') as f:
                topics = json.dump({'topics': self.__dict["topics"]}, f)

        return topic_d["id"]

    def add_data(self, topic_id, values):
        try:
            topic_d = next(i for i in self.__dict["topics"] if i["id"] == topic_id)
        except StopIteration:
            raise KeyError("Topic ID '" + topic_id + "' not found from database")
        fields = topic_d["fields"]

        data = DBConnection.generate_data_entry(topic_id, fields, values)
        self.__dict[topic_id].append(data)

    def get_topics(self):
        topics = self.__dict["topics"]
        return DBConnection.generate_topics_list(topics)

    def get_topic(self, topic_id):
        try:
            topic = next(i for i in self.__dict["topics"] if i["id"] == topic_id)
        except StopIteration:
            raise KeyError("Topic ID '" + topic_id + "' not found from database")

        return DBConnection.generate_topic_response(topic)


    def get_data(self, topic_id):
        try:
            topic_d = next(i for i in self.__dict["topics"] if i["id"] == topic_id)
        except StopIteration:
            raise KeyError("Topic ID '" + topic_id + "' not found from database")
        fields = topic_d["fields"]
        data = self.__dict[topic_id]

        return DBConnection.generate_data_response(data, fields)

ConnectionClass = DictConnection
