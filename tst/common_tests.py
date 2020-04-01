from datetime import datetime
from freezegun import freeze_time

def add_topic_affects_get_topic_output(self, C):
    topic_id = C.add_topic("topic")
    self.assertEqual(C.get_topic(topic_id)["name"], "topic")
    self.assertEqual(C.get_topics()[0]["name"], "topic")
    self.assertEqual(len(C.get_topics()), 1)

def cannot_add_data_to_undefined_topic(self, C):
    with self.assertRaises(KeyError):
        C.add_data("topic_id", {"key": "value"})

def cannot_add_data_with_non_matching_number_of_fields(self, C):
    topic_id = C.add_topic("topic", description="description", fields=["number"])
    with self.assertRaises(ValueError):
        C.add_data(topic_id, {"key1": "value1", "key2": "value2"})

def cannot_add_data_with_non_matching_fields(self, C):
    topic_id = C.add_topic("topic", description="description", fields=["number"])
    with self.assertRaises(ValueError):
        C.add_data(topic_id, {"key": "value"})

def add_data_affects_get_data_output(self, C):
    topic_id = C.add_topic("topic", description="description", fields=["number"])
    C.add_data(topic_id, {"number": 3})
    self.assertEqual(C.get_data(topic_id)[0]["number"], 3)
    self.assertEqual(len(C.get_data(topic_id)), 1)

def cannot_get_undefined_topic(self, C):
    with self.assertRaises(KeyError):
        C.get_topic("topic_id")

def cannot_get_data_of_undefined_topic(self, C):
    with self.assertRaises(KeyError):
        C.get_data("topic_id")

def can_get_data_since_until_limit(self, C):
    topic_id = C.add_topic("topic", description="description", fields=["number"])

    for i in range(10):
        with freeze_time(datetime(2020,1,1,1,i)):
            C.add_data(topic_id, {"number": 3})

    data = C.get_data(topic_id, since=datetime(2020,1,1,1,5))
    self.assertEqual(data[0].get('timestamp'), '2020-01-01T01:05:00Z')
    self.assertEqual(len(data), 5)

    data = C.get_data(topic_id, until=datetime(2020,1,1,1,5))
    self.assertEqual(data[0].get('timestamp'), '2020-01-01T01:00:00Z')
    self.assertEqual(data[-1].get('timestamp'), '2020-01-01T01:05:00Z')
    self.assertEqual(len(data), 6)

    data = C.get_data(topic_id, limit=5)
    self.assertEqual(data[0].get('timestamp'), '2020-01-01T01:05:00Z')
    self.assertEqual(len(data), 5)



tests = [
    add_topic_affects_get_topic_output,
    cannot_add_data_to_undefined_topic,
    cannot_add_data_with_non_matching_number_of_fields,
    cannot_add_data_with_non_matching_fields,
    add_data_affects_get_data_output,
    cannot_get_undefined_topic,
    cannot_get_data_of_undefined_topic,
    can_get_data_since_until_limit
]
