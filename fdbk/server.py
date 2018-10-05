from flask import Flask, jsonify, request, send_from_directory
from importlib import import_module

import argparse
import json
import os
import requests
import uuid

# Main:

__default_config = {
	"DBConnection": "DictConnection",
	"DBParameters": [],
	"AllowedActions": [
		"addData",
		"getData",
		"getTopics",
		"getTopic"
	],
	"ServeCWD": True
}

def __read_config(filename):
	if not filename:
		return __default_config
	with open(filename, "r") as f:
		return json.load(f)

def __generate_parser():
	parser = argparse.ArgumentParser()
	parser.add_argument("-c","--config-file",
		help="configuration file path",
		default="",
		type=str)
	parser.add_argument("--host",
		help="hosts to serve to (default = 0.0.0.0)",
		default="0.0.0.0",
		type=str)
	parser.add_argument("-p","--port",
		help="port to serve from (default = 8080)",
		default=8080,
		type=int)
	return parser

__args = __generate_parser().parse_args()
__config = __read_config(__args.config_file)

# Exports:

APP = Flask(__name__)

def start():
	APP.run(use_reloader=True, host=__args.host, port=__args.port, threaded=True)

# Helpers:

__InvalidTokenJSON = {
	"error": "Token not recognized"
}

__ActionNotAllowedJSON = {
	"error": "Action not allowed"
}

__DBConnectionMod = import_module("fdbk." + __config["DBConnection"])
__DBConnection = __DBConnectionMod.ConnectionClass(*(__config["DBParameters"]))

# API

if __config["ServeCWD"]:
	@APP.route('/')
	def index():
		return send_from_directory('.', 'index.html')

@APP.route('/add/topic', methods=["POST"])
def addTopic():
	if "addTopic" not in __config["AllowedActions"]:
		return jsonify(__ActionNotAllowedJSON), 403
	if __config["AddTokens"] and ("token" not in request.args or request.args["token"] not in __config["AddTokens"]):
		return jsonify(__InvalidTokenJSON), 403
	json_in = request.get_json()

	topic = json_in.pop("topic", None)
	if not topic:
		return jsonify({
			"error": "No 'topic' field in input data"
		}), 404

	try:
		__DBConnection.addTopic(topic, **json_in)
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
		"success": "Data successfully added to DB"
	})

@APP.route('/add/data/<topic>', methods=["POST"])
def addData(topic):
	if "addData" not in __config["AllowedActions"]:
		return jsonify(__ActionNotAllowedJSON), 403
	if __config["AddTokens"] and ("token" not in request.args or request.args["token"] not in __config["AddTokens"]):
		return jsonify(__InvalidTokenJSON), 403
	if not __DBConnection.getTopic(topic)["allow_api_submissions"]:
		return jsonify({
			"error": "Data submissions through API not allowed for topic '" + topic + "'"
		}), 403

	input = request.get_json()
	try:
		__DBConnection.addData(topic, input)
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

@APP.route('/get/topic/<topic>', methods=["GET"])
def getTopic(topic):
	if "getTopic" not in __config["AllowedActions"]:
		return jsonify(__ActionNotAllowedJSON), 403
	try:
		topic_json = __DBConnection.getTopic(topic)
		return jsonify(topic_json)
	except KeyError as e:
		return jsonify({
			"error": str(e)
		}), 404

@APP.route('/get/data/<topic>', methods=["GET"])
def getData(topic):
	if "getData" not in __config["AllowedActions"]:
		return jsonify(__ActionNotAllowedJSON), 403
	try:
		data = __DBConnection.getData(topic)
		return jsonify(data)
	except KeyError as e:
		return jsonify({
			"error": str(e)
		}), 404

if __name__ =='__main__':
	# TODO: This is for initial demo, please remove later
	try:
		__DBConnection.addTopic("IPA", "Taste review of this cool IPA!", ["stars","text"], ["stars", None], ["average", null], ["percent-stacked-bar", None], True)
	except KeyError:
		pass

	__DBConnection.addData("IPA", {
		"stars": 3,
		"text": "Solid work. Nothing too special."
	})

	start()
