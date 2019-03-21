class VisualizationFuncs(object):
	__FUNCS = [
		"horseshoe",
		"line"
	]

	def __contains__(self, item):
		return item in self.__FUNCS

	def __getitem__(self, key):
		if key == "horseshoe":
			return VisualizationFuncs.horseshoe
		if key == "line":
			return VisualizationFuncs.line
		return lambda data, field: None

	@staticmethod
	def horseshoe(data, field):
		field_data = [a[field] for a in data]

		return {
			"type": "horseshoe",
			"field": field,
			"data": [field_data.count(label) for label in set(field_data)],
			"labels": list(set(field_data))
		}

	@staticmethod
	def line(data, field):
		return {
			"type": "line",
			"field": field,
			"data": [{"x": a["timestamp"], "y": a[field]} for a in data],
		}
