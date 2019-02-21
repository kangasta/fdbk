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
		"last_truthy": lambda data, field: {
			"type": "last_truthy",
			"field": field,
			"value": [d for d in data if d[field]][-1]["timestamp"] if len([d for d in data if d[field]]) else None
		},
		"last_falsy": lambda data, field: {
			"type": "last_falsy",
			"field": field,
			"value": [d for d in data if not d[field]][-1]["timestamp"] if len([d for d in data if not d[field]]) else None
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
		"name",
		"id",
		"type",
		"description",
		"fields",
		"units",
		"summary",
		"visualization",
		"metadata",
		"form_submissions"
	]

	def addTopic(self, name, type_str="undefined", description="", fields=[], units=[], summary=[], visualization=[], metadata={}, form_submissions=False):
		'''Adds new topic to DB.

		Args:
			name: Name of the topic.
			type_str: Type of the topic, for example 'form' or 'sensor'.
			description: Description of the topic.
			fields: List of data field names included in the topic.
			units: List of units for field.
			summary: List of summary instructions for corresponding fields.
			visualization: List of visualization instructions for corresponding fields.
			metadata: Dict of metadata for topic
			form_submissions: Boolean to determine if data for this topic should be added through the API

		Returns:
			Topic ID of the newly created topic

		Raises:
			KeyError: Topic already exists in DB
		'''
		raise NotImplementedError("Functionality not implemented by selected DB connection")

	def addData(self, topic_id, values):
		'''Adds data under given topic in DB

		Args:
			topic_id: ID of the topic under which to add data.
			values: Dictionary with field names as keys and field value as value.

		Returns:
			None

		Raises:
			KeyError: Topic does not exist in DB
			ValueError: Values do not match those defined for the topic
		'''
		raise NotImplementedError("Functionality not implemented by selected DB connection")

	@staticmethod
	def generateDataEntry(topic_id, fields, values):
		'''Generates data entry to add to the DB

		Validates that the fields match to the ones specified by the provided topic ID. Adds topic ID and timestamp to the provides values entry.

		Args:
			topic_id: Topic ID to add to the entry
			fields: Fields to validate against
			values: Valued to add to the data entry

		Returns:
			Data entry dict with timestamp and topic ID

		Raises:
			ValueError: provided values do not match to the provided fields
		'''
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

		return data

	def getTopics(self):
		'''Gets list of topic dicts

		Returns:
			List of topic dicts
		'''
		raise NotImplementedError("Functionality not implemented by selected DB connection")

	@staticmethod
	def generateTopicsList(topics):
		''' Removes DB specific fields from the topics list

		Args:
			topics: List of DB entries

		Returns:
			Standardized topics list
		'''
		ret = []
		for topic in topics:
			ret.append(
				DBConnection.generateTopicResponse(topic)
			)
		return ret

	def getTopic(self, topic_id):
		'''Get topic dict by ID

		Args:
			topic_id: ID of the topic to find

		Returns:
			Topic dictionary with matching name

		Raises:
			KeyError: Topic does not exist in DB
		'''
		raise NotImplementedError("Functionality not implemented by selected DB connection")

	@staticmethod
	def generateTopicResponse(topic):
		''' Removes DB specific fields from the topic data

		Args:
			topics: DB entry

		Returns:
			Standardized topic dict
		'''
		topic_d = {}
		for field in DBConnection.TOPIC_FIELDS:
			topic_d[field] = topic[field]
		return topic_d

	def getData(self, topic_id):
		'''Get all data under given topic

		Args:
			topic_id: ID of the topic to find

		Returns:
			List of all data dicts under topic with matching name

		Raises:
			KeyError: Topic does not exist in DB
		'''
		raise NotImplementedError("Functionality not implemented by selected DB connection")

	@staticmethod
	def generateDataResponse(data, fields):
		''' Generate standardized data list from DB entries

		Standardizes the DB entries from the DB and converts the timestamps to ISO 8601 strings.

		Args:
			data: List of DB data entries
			fields: Fields to parse from DB data entries

		Returns:
			Standardized data list
		'''
		ret = []
		for d in data:
			ret.append({
				"topic_id": d["topic_id"],
				"timestamp": d["timestamp"].isoformat() + "Z"
			})
			for field in fields:
				ret[-1][field] = d[field]
		return ret

	def getLatest(self, topic_id):
		'''Get latest data element of given topic

		Note that this is an unoptimized implementation that wont be efficient for most databases. This method should be overridden by inheriting classes.

		Args:
			topic_id: ID of the topic to find

		Returns:
			Latest data dict under topic with matching name

		Raises:
			KeyError: Topic does not exist in DB
			IndexError: Topic has no data available

		'''
		return self.getData(topic_id)[-1]

	def getSummary(self, topic_id):
		'''Get summary of the topic data

		Args:
			topic_id: ID of the topic to get the summary of

		Returns:
			Dictionary with summary of the topic

		Raises:
			KeyError: Topic does not exist in DB
		'''
		data_d = self.getData(topic_id)
		topic_d = self.getTopic(topic_id)

		summary_d = {
			"topic": topic_d["name"],
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
