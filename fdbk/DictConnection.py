from datetime import datetime
from uuid import uuid4

from fdbk import DBConnection

class DictConnection(DBConnection):
	def __init__(self):
		self.__dict = {
			"topics": []
		}

	def addTopic(self, name, type_str="undefined", description="", fields=[], units=[], summary=[], visualization=[], metadata={}, form_submissions=False):
		topic_id = str(uuid4())

		self.__dict["topics"].append({
			"name": name,
			"id": topic_id,
			"type": type_str,
			"description": description,
			"fields": fields,
			"units": units,
			"summary": summary,
			"visualization": visualization,
			"metadata": metadata,
			"form_submissions": form_submissions
		})
		self.__dict[topic_id] = []

		return topic_id

	def addData(self, topic_id, values):
		try:
			topic_d = next(i for i in self.__dict["topics"] if i["id"] == topic_id)
		except StopIteration:
			raise KeyError("Topic ID '" + topic_id + "' not found from database")
		fields = topic_d["fields"]

		data = DBConnection.generateDataEntry(topic_id, fields, values)
		self.__dict[topic_id].append(data)

	def getTopics(self):
		topics = self.__dict["topics"]
		return DBConnection.generateTopicsList(topics)

	def getTopic(self, topic_id):
		try:
			topic = next(i for i in self.__dict["topics"] if i["id"] == topic_id)
		except StopIteration:
			raise KeyError("Topic ID '" + topic_id + "' not found from database")

		return DBConnection.generateTopicResponse(topic)


	def getData(self, topic_id):
		try:
			topic_d = next(i for i in self.__dict["topics"] if i["id"] == topic_id)
		except StopIteration:
			raise KeyError("Topic ID '" + topic_id + "' not found from database")
		fields = topic_d["fields"]
		data = self.__dict[topic_id]

		return DBConnection.generateDataResponse(data, fields)

ConnectionClass = DictConnection
