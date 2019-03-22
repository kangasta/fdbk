from flask import jsonify, request

class ServerHandlers(object):
	def __init__(self, db_connection, config):
		self.__db_connection = db_connection
		self.__config = config

		self.__invalid_token_json = {
			"error": "Token not recognized"
		}

		self.__action_not_allowed_json = {
			"error": "Action not allowed"
		}

	def addTopic(self):
		if "addTopic" not in self.__config["AllowedActions"]:
			return jsonify(self.__action_not_allowed_json), 403
		if "AddTokens" in self.__config and self.__config["AddTokens"] and ("token" not in request.args or request.args["token"] not in self.__config["AddTokens"]):
			return jsonify(self.__invalid_token_json), 403
		try:
			json_in = request.get_json()
		except:
			return jsonify({
				"error": "No topic data provided in request"
			}), 404

		topic = json_in.pop("name", None)
		type_str = json_in.pop("type", None)
		if not topic:
			return jsonify({
				"error": "No 'topic' field in input data"
			}), 404

		try:
			topic_id = self.__db_connection.addTopic(topic, type_str=type_str, **json_in)
		except KeyError as error:
			# Field not available in input data
			return jsonify({
				"error": str(error)
			}), 404
		except TypeError as error:
			return jsonify({
				"error": str(error)
			}), 400
		return jsonify({
			"topic_id": topic_id,
			"success": "Topic successfully added to DB"
		})

	def addData(self, topic_id):
		if "addData" not in self.__config["AllowedActions"]:
			return jsonify(self.__action_not_allowed_json), 403
		if "AddTokens" in self.__config and self.__config["AddTokens"] and ("token" not in request.args or request.args["token"] not in self.__config["AddTokens"]):
			return jsonify(self.__invalid_token_json), 403

		try:
			json_in = request.get_json()
		except:
			return jsonify({
				"error": "No topic data provided in request"
			}), 404
		try:
			self.__db_connection.addData(topic_id, json_in)
		except KeyError as error:
			# Topic not defined
			return jsonify({
				"error": str(error)
			}), 404
		except ValueError as error:
			# Fields do not match with topic
			return jsonify({
				"error": str(error)
			}), 400
		return jsonify({
			"success": "Data successfully added to DB"
		})

	def getTopics(self):
		if "getTopics" not in self.__config["AllowedActions"]:
			return jsonify(self.__action_not_allowed_json), 403
		return jsonify(self.__db_connection.getTopics())

	def getTopic(self, topic_id):
		if "getTopic" not in self.__config["AllowedActions"]:
			return jsonify(self.__action_not_allowed_json), 403
		try:
			topic_json = self.__db_connection.getTopic(topic_id)
			return jsonify(topic_json)
		except KeyError as error:
			return jsonify({
				"error": str(error)
			}), 404

	def getData(self, topic_id):
		if "getData" not in self.__config["AllowedActions"]:
			return jsonify(self.__action_not_allowed_json), 403
		try:
			data = self.__db_connection.getData(topic_id)
			return jsonify(data)
		except KeyError as error:
			return jsonify({
				"error": str(error)
			}), 404

	def getLatest(self, topic_id):
		if "getLatest" not in self.__config["AllowedActions"]:
			return jsonify(self.__action_not_allowed_json), 403
		try:
			data = self.__db_connection.getLatest(topic_id)
			return jsonify(data)
		except Exception as error:
			return jsonify({
				"error": str(error)
			}), 404

	def getSummary(self, topic_id):
		if "getSummary" not in self.__config["AllowedActions"]:
			return jsonify(self.__action_not_allowed_json), 403
		try:
			data = self.__db_connection.getSummary(topic_id)
			return jsonify(data)
		except KeyError as error:
			return jsonify({
				"error": str(error)
			}), 404

	def getComparison(self, topic_ids):
		if "getSummary" not in self.__config["AllowedActions"]:
			return jsonify(self.__action_not_allowed_json), 403
		try:
			data = self.__db_connection.getComparison(topic_ids.split(','))
			return jsonify(data)
		except KeyError as error:
			return jsonify({
				"error": str(error)
			}), 404

	def getOverview(self):
		if "getOverview" not in self.__config["AllowedActions"]:
			return jsonify(self.__action_not_allowed_json), 403
		try:
			data = self.__db_connection.getOverview()
			return jsonify(data)
		except KeyError as error:
			return jsonify({
				"error": str(error)
			}), 404
