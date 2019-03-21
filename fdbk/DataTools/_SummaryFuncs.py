from numbers import Number

class SummaryFuncs(object):
	__FUNCS = [
		"average",
		"latest",
		"last_truthy",
		"last_falsy"
	]

	def __contains__(self, item):
		return item in self.__FUNCS

	def __getitem__(self, key):
		if key == "average":
			return SummaryFuncs.average
		if key == "latest":
			return SummaryFuncs.latest
		if key == "last_truthy":
			return lambda data, field: SummaryFuncs.last(True, data, field)
		if key == "last_falsy":
			return lambda data, field: SummaryFuncs.last(False, data, field)
		return lambda data, field: None

	@staticmethod
	def average(data, field):
		filtered_data = [d[field] for d in data if isinstance(d[field], Number)]
		if not filtered_data:
			return None

		return {
			"type": "average",
			"field": field,
			"value": sum(i/float(len(filtered_data)) for i in filtered_data)
		}

	@staticmethod
	def latest(data, field):
		return {
			"type": "latest",
			"field": field,
			"value": data[-1][field] if data else None
		}

	@staticmethod
	def last(truthy_or_falsy, data, field):
		truthy_or_falsy = bool(truthy_or_falsy)
		filtered_data = [d for d in data if bool(d[field]) == truthy_or_falsy]
		if not filtered_data:
			return None

		type_str = "last_truthy" if truthy_or_falsy else "last_falsy"
		value = filtered_data[-1]["timestamp"]

		return {
			"type": type_str,
			"field": field,
			"value": value
		}
