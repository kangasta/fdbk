from datetime import datetime
from pymongo import MongoClient
from uuid import uuid4

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

	def addTopic(self, name, type_str="undefined", description="", fields=[], units=[], summary=[], visualization=[], metadata={}, form_submissions=False):
		with MongoClient(self.__mongo_url) as client:
			db = self.__get_db(client)

			topic_id = str(uuid4())

			db["topics"].insert_one({
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

			return topic_id

	def addData(self, topic_id, values):
		with MongoClient(self.__mongo_url) as client:
			db = self.__get_db(client)
			topics = db["topics"].find({"id": topic_id})
			if topics.count() != 1:
				raise KeyError("Topic ID '" + topic_id + "' not found from database '" + self.__db + "'")
			fields = topics[0]["fields"]
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

			db[topic_id].insert_one(data)

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

	def getTopic(self, topic_id):
		with MongoClient(self.__mongo_url) as client:
			db = self.__get_db(client)

			topics = db["topics"].find({"id": topic_id})
			if topics.count() < 1:
				raise KeyError("Topic ID '" + topic_id + "' not found from database '" + self.__db + "'")
			topic = topics[0]

			topic_d = {}
			for field in DBConnection.TOPIC_FIELDS:
				topic_d[field] = topic[field]
			return topic_d

	def getData(self, topic_id):
		with MongoClient(self.__mongo_url) as client:
			db = self.__get_db(client)

			topics = db["topics"].find({"id": topic_id})
			if topics.count() == 0:
				raise KeyError("Topic ID '" + topic_id + "' not found from database '" + self.__db + "'")
			fields = topics[0]["fields"]
			data = db[topic_id].find()

			ret = []
			for d in data:
				ret.append({
					"topic_id": d["topic_id"],
					"timestamp": d["timestamp"].isoformat()
				})
				for field in fields:
					ret[-1][field] = d[field]
			return ret

ConnectionClass = MongoConnection
