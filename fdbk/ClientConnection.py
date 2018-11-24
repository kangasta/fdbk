from datetime import datetime

import requests

from fdbk import DBConnection

class ClientConnection(DBConnection):
	def __init__(self, url, token=None):
		self.__url = url
		self.__token = token

	def addTopic(self, topic, type_str="undefined", description="", fields=[], units=[], summary=[], visualization=[], allow_api_submissions=True):
		requests.post(self.__url + "/add/topic", data={
			"topic": topic,
			"type": type_str,
			"description": description,
			"fields": fields,
			"units": units,
			"summary": summary,
			"visualization": visualization,
			"allow_api_submissions": allow_api_submissions
		})
		return None

	def addData(self, topic, values):
		requests.post(self.__url + "/add/data/" + topic, data=values)
		return None

	def getTopics(self):
		# TODO: Error handling
		return requests.get(self.__url + "/get/topics").json()

	def getTopic(self, topic):
		# TODO: Error handling
		return requests.get(self.__url + "/get/topic/" + topic).json()

	def getData(self, topic):
		# TODO: Error handling
		return requests.get(self.__url + "/get/data/" + topic).json()

ConnectionClass = ClientConnection
