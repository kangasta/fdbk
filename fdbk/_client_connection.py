import json
import requests

from fdbk import DBConnection

class ClientConnection(DBConnection):
    def __init__(self, url, token=None):
        self.__url = url
        self.__token = token

    def add_topic(self, name, **kwargs):
        response = requests.post(self.__url + "/topics", json=DBConnection.generate_topic_dict(name, **kwargs))

        if not response.ok:
            raise RuntimeError(json.dumps(response.json()))

        return response.json()["topic_id"]

    def add_data(self, topic_id, values):
        response = requests.post(self.__url + "/topics/" + topic_id + "/data", json=values)

        if not response.ok:
            raise RuntimeError(json.dumps(response.json()))

    def get_topics(self):
        # TODO: Error handling
        response = requests.get(self.__url + "/topics")

        if not response.ok:
            raise RuntimeError(json.dumps(response.json()))

        return response.json()

    def get_topic(self, topic_id):
        # TODO: Error handling
        response = requests.get(self.__url + "/topics" + topic_id)

        if not response.ok:
            raise RuntimeError(json.dumps(response.json()))

        return response.json()

    def get_data(self, topic_id):
        # TODO: Error handling
        response = requests.get(self.__url + "/topics/" + topic_id + "/data")

        if not response.ok:
            raise RuntimeError(json.dumps(response.json()))

        return response.json()

ConnectionClass = ClientConnection
