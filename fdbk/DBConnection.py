from datetime import datetime
from numbers import Number

class DBConnection(object):
	'''Base class for DB connections.
	'''
	SUMMARY_FUNCS = {
		"average": lambda data, field: {
			"type": "average",
			"field": field,
			"value": sum(i/float(len([d for d in data if isinstance(d[field], Number)])) for i in (a[field] for a in data) if isinstance(i, Number))
		},
		"latest": lambda data, field: {
			"type": "latest",
			"field": field,
			"value": data[-1][field] if len(data) else None
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
		"line": lambda data, field: {
			"type": "line",
			"field": field,
			"labels": [a["timestamp"] for a in data],
			"data": [a[field] for a in data]
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
		"form_submissions"
	]

	def addTopic(self, topic, type_str="undefined", description="", fields=[], units=[], summary=[], visualization=[], form_submissions=False):
		'''Adds new topic to DB.

		Args:
			topic: Name of the topic.
			type_str: Type of the topic, for example 'form' or 'sensor'.
			description: Description of the topic.
			fields: List of data field names included in the topic.
			units: List of units for field.
			summary: List of summary instructions for corresponding fields.
			visualization: List of visualization instructions for corresponding fields.
			form_submissions: Boolean to determine if data for this topic should be added through the API

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

	def getLatest(self, topic):
		'''Get latest data element of given topic

		Note that this is an unoptimized implementation that wont be efficient for most databases. This method should be overridden by inheriting classes.

		Args:
			topic: Name of the topic to find

		Returns:
			Latest data dict under topic with matching name

		Raises:
			KeyError: Topic does not exist in DB
			IndexError: Topic has no data available

		'''
		return self.getData(topic)[-1]

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

		for summary_item in topic_d["summary"]:
			if summary_item["method"] not in self.SUMMARY_FUNCS:
				summary_d["warnings"].append("The requested summary method '" + summary_item["method"] + "' is not supported.")
				continue
			if summary_item["field"] not in topic_d["fields"]:
				summary_d["warnings"].append("The requested field '" + summary_item["field"] + "' is undefined.")
				continue
			summary_d["summaries"].append(self.SUMMARY_FUNCS[summary_item["method"]](data_d, summary_item["field"]))

		for visualization_item in topic_d["visualization"]:
			if visualization_item["method"] not in self.VISUALIZATION_FUNCS:
				summary_d["warnings"].append("The requested visualization method '" + visualization_item["method"] + "' is not supported.")
				continue
			if visualization_item["field"] not in topic_d["fields"]:
				summary_d["warnings"].append("The requested field '" + visualization_item["field"] + "' is undefined.")
				continue
			summary_d["visualizations"].append(self.VISUALIZATION_FUNCS[visualization_item["method"]](data_d, visualization_item["field"]))

		return summary_d

ConnectionClass = DBConnection
