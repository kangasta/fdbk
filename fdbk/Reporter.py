import json
from importlib import import_module
from time import sleep

class Reporter(object):
	def __init__(self, data_source, db_connection='', db_parameters=[], topic_id=None, verbose=False):
		self.__data_source = data_source
		self.__topic_id = topic_id
		self.__verbose = verbose

		self.__create_client(db_connection, db_parameters)
		if self.__topic_id is None:
			self.__create_topic()

	def __create_client(self, db_connection, db_parameters):
		try:
			db_connection_mod = import_module("fdbk." + db_connection)
			self.__client = db_connection_mod.ConnectionClass(*db_parameters)
		except Exception as e:
			raise RuntimeError("Loading or creating fdbk DB connection failed: " + str(e))
		if self.__verbose:
			print("Created fdbk DB connection of type '" + db_connection + "' with parameters " + str(db_parameters))

	def __create_topic(self):
		topic_d = self.__data_source.topic

		if self.__verbose:
			print("Creating topic '" + topic_d["name"] + "' to fdbk")

		self.__topic_id = self.__client.addTopic(**topic_d)

	@property
	def connection(self):
		return self.__client

	@property
	def topic_id(self):
		return self.__topic_id

	def push(self, data):
		self.__client.addData(self.__topic_id, data)

		if self.__verbose:
			print("Push:\n" + json.dumps(data, indent=2, sort_keys=True))

	def start(self, interval=360, num_samples=60):
		try:
			while True:
				data = {}
				active_samples = num_samples

				for field in self.__data_source.topic["fields"]:
					data[field] = 0

				for _ in range(num_samples):
					sample = self.__data_source.data
					if sample is None:
						return
					if None in sample.values():
						# TODO warning for ignored samples
						active_samples -= 1
						continue
					for key in sample:
						data[key] += float(sample[key])
					sleep(float(interval)/num_samples)

				if active_samples > 0:
					for key in data:
						data[key] = float(data[key])/active_samples

					try:
						self.push(data)
					except Exception as e:
						if self.__verbose:
							print("Push failed: " + str(e))
				elif self.__verbose:
					print("Push skipped: No valid samples to average.")
		except KeyboardInterrupt:
			return
