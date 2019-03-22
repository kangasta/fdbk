from importlib import import_module
import json
import logging
import os
import uuid

from flask import Flask, jsonify, request, send_from_directory
import requests

from ._ServerHandlers import ServerHandlers

def generateApp(config=None, serve_cwd=True, log_level=logging.WARN):
	default_config = {
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

	config = config
	if not config:
		config = default_config
	elif isinstance(config, str):
		with open(config, "r") as f:
			config = json.load(f)
	elif not isinstance(config, dict):
		raise ValueError("Input configuration not recognized.")

	static_folder = os.path.join(os.getcwd(), "static") if config["ServeCWD"] else None
	app = Flask(__name__, static_folder=static_folder)

	db_connection_mod = import_module("fdbk." + config["DBConnection"])
	db_connection = db_connection_mod.ConnectionClass(*(config["DBParameters"]))

	handlers = ServerHandlers(db_connection, config)

	app.logger.setLevel(log_level)
	app.logger.info('Created "' + config["DBConnection"] + '" with parameters: ' + str(config["DBParameters"]))

	# API

	if config["ServeCWD"]:
		@app.route('/')
		def index():
			return send_from_directory(os.getcwd(), 'index.html')

	@app.route('/topics', methods=['GET', 'POST'])
	def topics():
		if request.method == 'GET':
			return handlers.getTopics()
		if request.method == 'POST':
			return handlers.addTopic()

	@app.route('/topics/<topic_id>', methods=['GET'])
	def topicsGet(topic_id):
		return handlers.getTopic(topic_id)

	@app.route('/topics/<topic_id>/data', methods=['GET', 'POST'])
	def data(topic_id):
		if request.method == 'GET':
			return handlers.getData(topic_id)
		if request.method == 'POST':
			return handlers.addData(topic_id)

	@app.route('/topics/<topic_id>/data/latest', methods=['GET', 'POST'])
	def latest(topic_id):
		return handlers.getLatest(topic_id)

	@app.route('/topics/<topic_id>/summary', methods=['GET'])
	def summary(topic_id):
		return handlers.getSummary(topic_id)

	@app.route('/comparison/<topic_ids>', methods=['GET'])
	def comparison(topic_ids):
		return handlers.getComparison(topic_ids)

	@app.route('/overview', methods=['GET'])
	def overview():
		return handlers.getOverview()

	return app
