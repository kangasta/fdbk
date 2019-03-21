from fdbk import DBConnection

class DictConnection(DBConnection):
	def __init__(self):
		self.__dict = {
			"topics": []
		}

	def addTopic(self, name, **kwargs):
		topic_d = DBConnection.generateTopicDict(name, add_id=True, **kwargs)

		self.__dict["topics"].append(topic_d)
		self.__dict[topic_d["id"]] = []

		return topic_d["id"]

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
