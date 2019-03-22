import json
import requests

from fdbk import DBConnection

class ClientConnection(DBConnection):
	def __init__(self, url, token=None):
		self.__url = url
		self.__token = token

	def addTopic(self, name, **kwargs):
		response = requests.post(self.__url + "/topics", json=DBConnection.generateTopicDict(name, **kwargs))

		if not response.ok:
			raise RuntimeError(json.dumps(response.json()))

		return response.json()["topic_id"]

	def addData(self, topic_id, values):
		response = requests.post(self.__url + "/topics/" + topic_id + "/data", json=values)

		if not response.ok:
			raise RuntimeError(json.dumps(response.json()))

	def getTopics(self):
		# TODO: Error handling
		response = requests.get(self.__url + "/topics")

		if not response.ok:
			raise RuntimeError(json.dumps(response.json()))

		return response.json()

	def getTopic(self, topic_id):
		# TODO: Error handling
		response = requests.get(self.__url + "/topics" + topic_id)

		if not response.ok:
			raise RuntimeError(json.dumps(response.json()))

		return response.json()

	def getData(self, topic_id):
		# TODO: Error handling
		response = requests.get(self.__url + "/topics/" + topic_id + "/data")

		if not response.ok:
			raise RuntimeError(json.dumps(response.json()))

		return response.json()

ConnectionClass = ClientConnection
