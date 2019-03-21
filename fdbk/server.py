from importlib import import_module
import json, os, uuid

from flask import Flask, jsonify, request, send_from_directory
import requests

def generate_app(config=None, serve_cwd=True):
	__DefaultConfig = {
		"DBConnection": "DictConnection",
		"DBParameters": [],
		"AllowedActions": [
			"addData",
			"addTopic",
			"getComparison",
			"getData",
			"getLatest",
			"getOverview",
			"getSummary",
			"getTopics",
			"getTopic"
		],
		"ServeCWD": serve_cwd
	}

	__InvalidTokenJSON = {
		"error": "Token not recognized"
	}

	__ActionNotAllowedJSON = {
		"error": "Action not allowed"
	}

	__config = config
	if not __config:
		__config = __DefaultConfig
	elif isinstance(__config, str):
		with open(__config, "r") as f:
			__config = json.load(f)
	elif not isinstance(__config, dict):
		raise ValueError("Input configuration not recognized.")

	static_folder = os.path.join(os.getcwd(), "static") if __config["ServeCWD"] else None
	APP = Flask(__name__, static_folder=static_folder)

	__DBConnectionMod = import_module("fdbk." + __config["DBConnection"])
	__DBConnection = __DBConnectionMod.ConnectionClass(*(__config["DBParameters"]))

	# API

	if __config["ServeCWD"]:
		@APP.route('/')
		def index():
			return send_from_directory(os.getcwd(), 'index.html')

	@APP.route('/add/topic', methods=["POST"])
	def addTopic():
		if "addTopic" not in __config["AllowedActions"]:
			return jsonify(__ActionNotAllowedJSON), 403
		if "AddTokens" in __config and __config["AddTokens"] and ("token" not in request.args or request.args["token"] not in __config["AddTokens"]):
			return jsonify(__InvalidTokenJSON), 403
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
			topic_id = __DBConnection.addTopic(topic, type_str=type_str, **json_in)
		except KeyError as e:
			# Field not available in input data
			return jsonify({
				"error": str(e)
			}), 404
		except TypeError as e:
			return jsonify({
				"error": str(e)
			}), 400
		return jsonify({
			"topic_id": topic_id,
			"success": "Topic successfully added to DB"
		})

	@APP.route('/add/data/<topic_id>', methods=["POST"])
	def addData(topic_id):
		if "addData" not in __config["AllowedActions"]:
			return jsonify(__ActionNotAllowedJSON), 403
		if "AddTokens" in __config and __config["AddTokens"] and ("token" not in request.args or request.args["token"] not in __config["AddTokens"]):
			return jsonify(__InvalidTokenJSON), 403

		try:
			json_in = request.get_json()
		except:
			return jsonify({
				"error": "No topic data provided in request"
			}), 404
		try:
			__DBConnection.addData(topic_id, json_in)
		except KeyError as e:
			# Topic not defined
			return jsonify({
				"error": str(e)
			}), 404
		except ValueError as e:
			# Fields do not match with topic
			return jsonify({
				"error": str(e)
			}), 400
		return jsonify({
			"success": "Data successfully added to DB"
		})

	@APP.route('/get/topics', methods=["GET"])
	def getTopics():
		if "getTopics" not in __config["AllowedActions"]:
			return jsonify(__ActionNotAllowedJSON), 403
		return jsonify(__DBConnection.getTopics())

	@APP.route('/get/topic/<topic_id>', methods=["GET"])
	def getTopic(topic_id):
		if "getTopic" not in __config["AllowedActions"]:
			return jsonify(__ActionNotAllowedJSON), 403
		try:
			topic_json = __DBConnection.getTopic(topic_id)
			return jsonify(topic_json)
		except KeyError as e:
			return jsonify({
				"error": str(e)
			}), 404

	@APP.route('/get/data/<topic_id>', methods=["GET"])
	def getData(topic_id):
		if "getData" not in __config["AllowedActions"]:
			return jsonify(__ActionNotAllowedJSON), 403
		try:
			data = __DBConnection.getData(topic_id)
			return jsonify(data)
		except KeyError as e:
			return jsonify({
				"error": str(e)
			}), 404

	@APP.route('/get/data/latest/<topic_id>', methods=["GET"])
	def getLatest(topic_id):
		if "getLatest" not in __config["AllowedActions"]:
			return jsonify(__ActionNotAllowedJSON), 403
		try:
			data = __DBConnection.getLatest(topic_id)
			return jsonify(data)
		except Exception as e:
			return jsonify({
				"error": str(e)
			}), 404

	@APP.route('/get/summary/<topic_id>', methods=["GET"])
	def getSummary(topic_id):
		if "getSummary" not in __config["AllowedActions"]:
			return jsonify(__ActionNotAllowedJSON), 403
		try:
			data = __DBConnection.getSummary(topic_id)
			return jsonify(data)
		except KeyError as e:
			return jsonify({
				"error": str(e)
			}), 404

	@APP.route('/get/comparison/<topic_ids>', methods=["GET"])
	def getComparison(topic_ids):
		if "getSummary" not in __config["AllowedActions"]:
			return jsonify(__ActionNotAllowedJSON), 403
		try:
			data = __DBConnection.getComparison(topic_ids.split(','))
			return jsonify(data)
		except KeyError as e:
			return jsonify({
				"error": str(e)
			}), 404

	@APP.route('/get/overview', methods=["GET"])
	def getOverview():
		if "getOverview" not in __config["AllowedActions"]:
			return jsonify(__ActionNotAllowedJSON), 403
		try:
			data = __DBConnection.getOverview()
			return jsonify(data)
		except KeyError as e:
			return jsonify({
				"error": str(e)
			}), 404

	return APP
