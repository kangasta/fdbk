from datetime import datetime
from pymongo import MongoClient

from fdbk import DBConnection

class MongoConnection(DBConnection):
	def __init__(self, mongo_url, db="default_db", username=None, password=None, auth_source="admin"):
		self.__mongo_url = mongo_url
		self.__db = db
		self.__username = username
		self.__password = password
		self.__auth_source = auth_source

	def __get_db(self, client):
		db = client[self.__db]
		if self.__username and self.__password:
			db.authenticate(self.__username, self.__password, source=self.__auth_source)
		return db

	def addTopic(self, topic, type_str="undefined", description="", fields=[], units=[], summary=[], visualization=[], allow_api_submissions=True):
		with MongoClient(self.__mongo_url) as client:
			db = self.__get_db(client)

			if db["topics"].find({"topic": topic}).count() > 0 or topic in db.list_collection_names():
				raise KeyError("Topic '" + topic + "' already exists in database '" + self.__db + "'")

			db["topics"].insert({
				"topic": topic,
				"type": type_str,
				"description": description,
				"fields": fields,
				"units": units,
				"summary": summary,
				"visualization": visualization,
				"allow_api_submissions": allow_api_submissions
			})

	def addData(self, topic, values):
		with MongoClient(self.__mongo_url) as client:
			db = self.__get_db(client)
			topics = db["topics"].find({"topic": topic})
			if topics.count() != 1:
				raise KeyError("Topic '" + topic + "' not found from database '" + self.__db + "'")
			fields = topics[0]["fields"]
			if len(fields) != len(values):
				raise ValueError("The number of given values does not match with the number of fields defined for topic")

			# TODO: validate to match topic fields
			data = {
				"topic": topic,
				"timestamp": datetime.utcnow()
			}
			for field in fields:
				if field not in values.keys():
					raise ValueError("Value for field '" + field + "' not present in input data")
				data[field] = values[field]

			db[topic].insert(data)

	def getTopics(self):
		with MongoClient(self.__mongo_url) as client:
			db = self.__get_db(client)

			topics = db["topics"].find()

			ret = []
			for topic in topics:
				topic_d = {}
				for field in DBConnection.TOPIC_FIELDS:
					topic_d[field] = topic[field]
				ret.append(topic_d)
			return ret

	def getTopic(self, topic):
		with MongoClient(self.__mongo_url) as client:
			db = self.__get_db(client)

			topics = db["topics"].find({"topic": topic})
			if topics.count() < 1:
				raise KeyError("Topic '" + topic + "' not found from database '" + self.__db + "'")
			topic = topics[0]

			topic_d = {}
			for field in DBConnection.TOPIC_FIELDS:
				topic_d[field] = topic[field]
			return topic_d

	def getData(self, topic):
		with MongoClient(self.__mongo_url) as client:
			db = self.__get_db(client)

			topics = db["topics"].find({"topic": topic})
			if topics.count() == 0:
				raise KeyError("Topic '" + topic + "' not found from database '" + self.__db + "'")
			fields = topics[0]["fields"]
			data = db[topic].find()

			ret = []
			for d in data:
				ret.append({
					"topic": d["topic"],
					"timestamp": d["timestamp"].isoformat()
				})
				for field in fields:
					ret[-1][field] = d[field]
			return ret

ConnectionClass = MongoConnection

if __name__ == "__main__":
	MG = MongoConnection("172.20.0.3", "feedback")

	print(MG.getTopics())
	try:
		print(MG.getData("IPA"))
	except KeyError as e:
		print(e)

	MG.addTopic("IPA", "Taste review of this cool IPA!", ["stars","text"], ["stars", None])

	try:
		MG.addData("IPA", {"polarity": +1, "text": "Taste is awesome!"})
	except ValueError as e:
		print(e)
	MG.addData("IPA", {"stars": 5, "text": "Taste is awesome!"})
	MG.addData("IPA", {"stars": 3, "text": "Taste is average."})
	MG.addData("IPA", {"stars": 2, "text": "Taste is meh."})

	print(MG.getTopics())
	print(MG.getData("IPA"))
