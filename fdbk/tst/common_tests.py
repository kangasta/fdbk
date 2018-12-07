def add_topic_affects_get_topic_output(self, C):
	topic_id = C.addTopic("topic")
	self.assertEqual(C.getTopic(topic_id)["name"], "topic")
	self.assertEqual(C.getTopics()[0]["name"], "topic")
	self.assertEqual(len(C.getTopics()), 1)

def cannot_add_data_to_undefined_topic(self, C):
	with self.assertRaises(KeyError):
		C.addData("topic_id", {"key": "value"})

def cannot_add_data_with_non_matching_number_of_fields(self, C):
	topic_id = C.addTopic("topic", description="description", fields=["number"])
	with self.assertRaises(ValueError):
		C.addData(topic_id, {"key1": "value1", "key2": "value2"})

def cannot_add_data_with_non_matching_fields(self, C):
	topic_id = C.addTopic("topic", description="description", fields=["number"])
	with self.assertRaises(ValueError):
		C.addData(topic_id, {"key": "value"})

def add_data_affects_get_data_output(self, C):
	topic_id = C.addTopic("topic", description="description", fields=["number"])
	C.addData(topic_id, {"number": 3})
	self.assertEqual(C.getData(topic_id)[0]["number"], 3)
	self.assertEqual(len(C.getData(topic_id)), 1)

def cannot_get_undefined_topic(self, C):
	with self.assertRaises(KeyError):
		C.getTopic("topic_id")

def cannot_get_data_of_undefined_topic(self, C):
	with self.assertRaises(KeyError):
		C.getData("topic_id")

tests = [
	add_topic_affects_get_topic_output,
	cannot_add_data_to_undefined_topic,
	cannot_add_data_with_non_matching_number_of_fields,
	cannot_add_data_with_non_matching_fields,
	add_data_affects_get_data_output,
	cannot_get_undefined_topic,
	cannot_get_data_of_undefined_topic
]
