from datetime import datetime

import json
import requests

from fdbk import DBConnection

class ClientConnection(DBConnection):
	def __init__(self, url, token=None):
		self.__url = url
		self.__token = token

	def addTopic(self, topic, type_str="undefined", description="", fields=[], units=[], summary=[], visualization=[], form_submissions=False):
		r = requests.post(self.__url + "/add/topic", json={
			"topic": topic,
			"type": type_str,
			"description": description,
			"fields": fields,
			"units": units,
			"summary": summary,
			"visualization": visualization,
			"form_submissions": form_submissions
		})
		if r.status_code != requests.codes.ok:
			raise RuntimeError(json.dumps(r.json()))
		return None

	def addData(self, topic, values):
		r = requests.post(self.__url + "/add/data/" + topic, json=values)
		if r.status_code != requests.codes.ok:
			raise RuntimeError(json.dumps(r.json()))
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
