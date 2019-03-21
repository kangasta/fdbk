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

	def addTopic(self, name, **kwargs):
		with MongoClient(self.__mongo_url) as client:
			db = self.__get_db(client)

			topic_d = DBConnection.generateTopicDict(name, add_id=True, **kwargs)

			db["topics"].insert_one(topic_d)

			return topic_d["id"]

	def addData(self, topic_id, values):
		with MongoClient(self.__mongo_url) as client:
			db = self.__get_db(client)
			topics = db["topics"].find({"id": topic_id})
			if topics.count() != 1:
				raise KeyError("Topic ID '" + topic_id + "' not found from database '" + self.__db + "'")
			fields = topics[0]["fields"]

			data = DBConnection.generateDataEntry(topic_id, fields, values)
			db[topic_id].insert_one(data)

	def getTopics(self):
		with MongoClient(self.__mongo_url) as client:
			db = self.__get_db(client)

			topics = db["topics"].find()
			return DBConnection.generateTopicsList(topics)

	def getTopic(self, topic_id):
		with MongoClient(self.__mongo_url) as client:
			db = self.__get_db(client)

			topics = db["topics"].find({"id": topic_id})
			if topics.count() < 1:
				raise KeyError("Topic ID '" + topic_id + "' not found from database '" + self.__db + "'")
			topic = topics[0]

			return DBConnection.generateTopicResponse(topic)

	def getData(self, topic_id):
		with MongoClient(self.__mongo_url) as client:
			db = self.__get_db(client)

			topics = db["topics"].find({"id": topic_id})
			if topics.count() == 0:
				raise KeyError("Topic ID '" + topic_id + "' not found from database '" + self.__db + "'")
			fields = topics[0]["fields"]
			data = db[topic_id].find()

			return DBConnection.generateDataResponse(data, fields)

ConnectionClass = MongoConnection
