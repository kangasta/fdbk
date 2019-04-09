from threading import Timer

from influxdb import InfluxDBClient

from fdbk import DBConnection, Utils

class InfluxConnection(DBConnection):
	class InfluxDBClientWrapper(InfluxDBClient):
		def __enter__(self):
			return self

		def __exit__(self, type, value, tb):
			Timer(5, self.close)
			return self

	def __init__(self, influx_url, db="default_db", username=None, password=None, topics_db='DictConnection', *topics_db_parameters):
		self.__influx_url = influx_url
		self.__db = db
		self.__username = username
		self.__password = password

		self.__ensure_db_exists()

		self.__topics_connection = Utils.create_db_connection(topics_db, topics_db_parameters)

	def __get_client(self):
		return InfluxConnection.InfluxDBClientWrapper(
			host=self.__influx_url,
			port=8086,
			username=self.__username,
			password=self.__password
		)

	def __ensure_db_exists(self):
		with self.__get_client() as client:
			if self.__db not in (db['name'] for db in client.get_list_database()):
				client.create_database(self.__db)

	def addTopic(self, name, **kwargs):
		if 'type_str' not in kwargs:
			kwargs['type_str'] = 'undefined'
		return self.__topics_connection.addTopic(name, **kwargs)

	def addData(self, topic_id, values):
		try:
			topic_d = self.getTopic(topic_id)
		except:
			raise KeyError("Topic ID '" + topic_id + "' not found from database '" + self.__db + "'")

		with self.__get_client() as client:
			fields = topic_d["fields"]

			data = DBConnection.generateDataEntry(topic_id, fields, values)
			data.pop('timestamp')
			data.pop('topic_id')

			client.write_points([{
				'measurement': topic_d['type'],
				'tags': {
					'topic_id': topic_id
				},
				'fields': data
			}], database=self.__db)

	def getTopics(self):
		return self.__topics_connection.getTopics()

	def getTopic(self, topic_id):
		return self.__topics_connection.getTopic(topic_id)

	def getData(self, topic_id):
		try:
			topic_d = self.getTopic(topic_id)
		except:
			raise KeyError("Topic ID '" + topic_id + "' not found from database '" + self.__db + "'")

		def time_to_timestamp(data_d):
			data_d["timestamp"] = data_d.pop("time")
			return data_d

		query_str = "select * from " + topic_d["type"] + " where topic_id='" + topic_id + "'"

		with self.__get_client() as client:
			return list(map(time_to_timestamp, client.query(query_str, database=self.__db).get_points()))

ConnectionClass = InfluxConnection
