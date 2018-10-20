class DBConnection(object):
	'''Base class for DB connections.
	'''
	SUMMARY_FUNCS = {
		"average": lambda data, field: {
			"type": "average",
			"field": field,
			"value": sum(i/float(len(data)) for i in (a[field] for a in data))
		},
		None: lambda data, field: None
	}

	VISUALIZATION_FUNCS = {
		"horseshoe": lambda data, field: {
			"type": "horseshoe",
			"field": field,
			"data": [[a[field] for a in data].count(label) for label in set((a[field] for a in data))],
			"labels": list(set((a[field] for a in data)))
		},
		None: lambda data, field: None
	}

	TOPIC_FIELDS = [
		"topic",
		"type",
		"description",
		"fields",
		"units",
		"summary",
		"visualization",
		"allow_api_submissions"
	]

	def addTopic(self, topic, type_str="undefined", description="", fields=[], units=[], summary=[], visualization=[], allow_api_submissions=True):
		'''Adds new topic to DB.

		Args:
			topic: Name of the topic.
			type_str: Type of the topic, for example 'form' or 'sensor'.
			description: Description of the topic.
			fields: List of data field names included in the topic.
			units: List of units for corresponding field.
			summary: List of summary instructions for corresponding fields.
			visualization: List of visualization instructions for corresponding fields.
			allow_api_submissions: Boolean to determine if data for this topic should be added through the API

		Returns:
			None

		Raises:
			KeyError: Topic already exists in DB
		'''
		raise NotImplementedError("Functionality not implemented by selected DB connection")

	def addData(self, topic, values):
		'''Adds data under given topic in DB

		Args:
			topic: Name of the topic under which to add data.
			values:	Dictionary with field names as keys and field value as value.

		Returns:
			None

		Raises:
			KeyError: Topic does not exist in DB
			ValueError: Values do not match those defined for the topic
		'''
		raise NotImplementedError("Functionality not implemented by selected DB connection")

	def getTopics(self):
		'''Gets list of topic dicts

		Returns:
			List of topic dicts
		'''
		raise NotImplementedError("Functionality not implemented by selected DB connection")

	def getTopic(self, topic):
		'''Get topic dict by name

		Args:
			topic: Name of the topic to find

		Returns:
			Topic dictionary with matching name

		Raises:
			KeyError: Topic does not exist in DB
		'''
		raise NotImplementedError("Functionality not implemented by selected DB connection")

	def getData(self, topic):
		'''Get all data under given topic

		Args:
			topic: Name of the topic to find

		Returns:
			List of all data dicts under topic with matching name

		Raises:
			KeyError: Topic does not exist in DB
		'''
		raise NotImplementedError("Functionality not implemented by selected DB connection")

	def getSummary(self, topic):
		'''Get summary of the topic data

		Args:
			topic: Name of the topic to get the summary of

		Returns:
			Dictionary with summary of the topic

		Raises:
			KeyError: Topic does not exist in DB
		'''
		data_d = self.getData(topic)
		topic_d = self.getTopic(topic)

		summary_d = {
			"topic": topic_d["topic"],
			"description": topic_d["description"],
			"units": topic_d["units"],
			"num_entries": len(data_d),
			"summaries": [],
			"visualizations": [],
			"warnings": []
		}

		for i,field in enumerate(topic_d["fields"]):
			try:
				summary_d["summaries"].append(self.SUMMARY_FUNCS[topic_d["summary"][i]](data_d, field))
			except KeyError:
				summary_d["warnings"].append("The requested summary method '" + topic_d["summary"][i] + "' is not supported.")
				summary_d["summaries"].append(None)

			try:
				summary_d["visualizations"].append(self.VISUALIZATION_FUNCS[topic_d["visualization"][i]](data_d, field))
			except KeyError:
				summary_d["warnings"].append("The requested visualization method '" + topic_d["visualization"][i] + "' is not supported.")
				summary_d["visualizations"].append(None)

		return summary_d

ConnectionClass = DBConnection
