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
		if len(fields) != len(values):
			raise ValueError("The number of given values does not match with the number of fields defined for topic")

		data = {
			"topic_id": topic_id,
			"timestamp": datetime.utcnow()
		}
		for field in fields:
			if field not in values.keys():
				raise ValueError("Value for field '" + field + "' not present in input data")
			data[field] = values[field]

		self.__dict[topic_id].append(data)

	def getTopics(self):
		topics = self.__dict["topics"]

		ret = []
		for topic in topics:
			topic_d = {}
			for field in DBConnection.TOPIC_FIELDS:
				topic_d[field] = topic[field]
			ret.append(topic_d)
		return ret

	def getTopic(self, topic_id):
		try:
			topic_d = next(i for i in self.__dict["topics"] if i["id"] == topic_id)
		except StopIteration:
			raise KeyError("Topic ID '" + topic_id + "' not found from database")

		topic = {}
		for field in DBConnection.TOPIC_FIELDS:
			topic[field] = topic_d[field]
		return topic

	def getData(self, topic_id):
		try:
			topic_d = next(i for i in self.__dict["topics"] if i["id"] == topic_id)
		except StopIteration:
			raise KeyError("Topic ID '" + topic_id + "' not found from database")
		fields = topic_d["fields"]
		data = self.__dict[topic_id]

		ret = []
		for d in data:
			ret.append({
				"topic_id": d["topic_id"],
				"timestamp": d["timestamp"].isoformat() + "Z"
			})
			for field in fields:
				ret[-1][field] = d[field]
		return ret

ConnectionClass = DictConnection
