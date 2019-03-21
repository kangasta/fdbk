import json
import requests

from fdbk import DBConnection

class ClientConnection(DBConnection):
	def __init__(self, url, token=None):
		self.__url = url
		self.__token = token

	def addTopic(self, name, **kwargs):
		r = requests.post(self.__url + "/add/topic", json=DBConnection.generateTopicDict(name, **kwargs))
		if r.status_code != requests.codes.ok:
			raise RuntimeError(json.dumps(r.json()))
		return r.json()["topic_id"]

	def addData(self, topic_id, values):
		r = requests.post(self.__url + "/add/data/" + topic_id, json=values)
		if r.status_code != requests.codes.ok:
			raise RuntimeError(json.dumps(r.json()))

	def getTopics(self):
		# TODO: Error handling
		return requests.get(self.__url + "/get/topics").json()

	def getTopic(self, topic_id):
		# TODO: Error handling
		return requests.get(self.__url + "/get/topic/" + topic_id).json()

	def getData(self, topic_id):
		# TODO: Error handling
		return requests.get(self.__url + "/get/data/" + topic_id).json()

ConnectionClass = ClientConnection
