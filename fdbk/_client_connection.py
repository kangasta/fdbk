'''DB connection to use with provided development server
'''

import json
import requests

from fdbk import DBConnection
from fdbk.utils import generate_topic_dict


class ClientConnection(DBConnection):
    '''DB connection to use with provided development server
    '''

    def __init__(self, url, token=None):
        self.__url = url
        self.__token = token

    @staticmethod
    def _get_overwrite_query(overwrite):
        if not overwrite:
            return ""
        return "?overwrite=true"

    def add_topic(self, name, overwrite=False, **kwargs):
        query = self._get_overwrite_query(overwrite)
        response = requests.post(
            self.__url + f"/topics{query}",
            json=generate_topic_dict(
                name,
                add_id=False,
                **kwargs))

        if not response.ok:
            raise RuntimeError(json.dumps(response.json()))

        return response.json()["topic_id"]

    def add_data(self, topic_id, values, overwrite=False):
        query = self._get_overwrite_query(overwrite)
        response = requests.post(
            self.__url + f"/topics/{topic_id}/data{query}", json=values)

        if not response.ok:
            raise RuntimeError(json.dumps(response.json()))

        return response.json()["timestamp"]

    def get_topics(self, type_=None, template=None):
        # TODO: Error handling
        query = []
        if type_:
            query.append(f"type={type_}")
        if template:
            query.append(f"template={template}")
        query = '&'.join(query)
        query = f"?{query}" if query else ""
        response = requests.get(f"{self.__url}/topics{query}")

        if not response.ok:
            raise RuntimeError(json.dumps(response.json()))

        return response.json()

    def get_topic(self, topic_id):
        # TODO: Error handling
        response = requests.get(f"{self.__url}/topics/{topic_id}")

        if not response.ok:
            raise RuntimeError(json.dumps(response.json()))

        return response.json()

    def get_data(self, topic_id, since=None, until=None, limit=None):
        # TODO: Error handling
        query = (
            "" if not since else f"since={since.isoformat()}Z",
            "" if not until else f"until={until.isoformat()}Z",
            "" if not limit else f"limit={limit}",
        )
        query = "&".join(i for i in query if i)
        query = f"?{query}" if query else ""
        response = requests.get(f"{self.__url}/topics/{topic_id}/data{query}")

        if not response.ok:
            raise RuntimeError(json.dumps(response.json()))

        return response.json()


ConnectionClass = ClientConnection
