# pylint: disable=no-member

from datetime import datetime

from freezegun import freeze_time


class CommonTest:
    def test_add_topic_affects_get_topic_output(self):
        topic_id = self.C.add_topic("topic")
        self.assertEqual(self.C.get_topic(topic_id)["name"], "topic")
        self.assertEqual(self.C.get_topics()[0]["name"], "topic")
        self.assertEqual(len(self.C.get_topics()), 1)

    def test_cannot_add_data_to_undefined_topic(self):
        with self.assertRaises(KeyError):
            self.C.add_data("topic_id", {"key": "value"})

    def test_cannot_add_data_with_non_matching_number_of_fields(self):
        topic_id = self.C.add_topic(
            "topic",
            description="description",
            fields=["number"])
        with self.assertRaises(ValueError):
            self.C.add_data(topic_id, {"key1": "value1", "key2": "value2"})

    def test_cannot_add_data_with_non_matching_fields(self):
        topic_id = self.C.add_topic(
            "topic",
            description="description",
            fields=["number"])
        with self.assertRaises(ValueError):
            self.C.add_data(topic_id, {"key": "value"})

    def test_add_data_affects_get_data_output(self):
        topic_id = self.C.add_topic(
            "topic",
            description="description",
            fields=["number"])
        self.C.add_data(topic_id, {"number": 3})
        self.assertEqual(self.C.get_data(topic_id)[0]["number"], 3)
        self.assertEqual(len(self.C.get_data(topic_id)), 1)

    def test_cannot_get_undefined_topic(self):
        with self.assertRaises(KeyError):
            self.C.get_topic("topic_id")

    def test_cannot_get_data_of_undefined_topic(self):
        with self.assertRaises(KeyError):
            self.C.get_data("topic_id")

    def test_can_get_data_since_until_limit(self):
        topic_id = self.C.add_topic(
            "topic",
            description="description",
            fields=["number"])

        for i in range(10):
            with freeze_time(datetime(2020, 1, 1, 1, i)):
                self.C.add_data(topic_id, {"number": 3})

        data = self.C.get_data(topic_id, since=datetime(2020, 1, 1, 1, 5))
        self.assertEqual(data[0].get('timestamp'), '2020-01-01T01:05:00Z')
        self.assertEqual(len(data), 5)

        data = self.C.get_data(topic_id, until=datetime(2020, 1, 1, 1, 5))
        self.assertEqual(data[0].get('timestamp'), '2020-01-01T01:00:00Z')
        self.assertEqual(data[-1].get('timestamp'), '2020-01-01T01:05:00Z')
        self.assertEqual(len(data), 6)

        data = self.C.get_data(topic_id, limit=5)
        self.assertEqual(data[0].get('timestamp'), '2020-01-01T01:05:00Z')
        self.assertEqual(len(data), 5)