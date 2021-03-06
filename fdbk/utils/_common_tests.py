# pylint: disable=no-member

from datetime import datetime

try:
    from freezegun import freeze_time
except ImportError:  # pragma: no cover
    pass


class CommonTest:
    def test_add_topic_affects_get_topic_output(self):
        topic_id = self.C.add_topic("topic")
        self.assertEqual(self.C.get_topic(topic_id)["name"], "topic")
        self.assertEqual(self.C.get_topics()[0]["name"], "topic")
        self.assertEqual(len(self.C.get_topics()), 1)

    def test_cannot_add_data_to_undefined_topic(self):
        with self.assertRaises(KeyError):
            self.C.add_data("topic_id", {"key": "value"})

    def test_cannot_add_duplicate_topic_unless_overwrite(self):
        topic_id = self.C.add_topic("topic", description='1')

        with self.assertRaises(KeyError):
            self.C.add_topic("topic", description='2', id_str=topic_id)

        self.C.add_topic(
            "topic",
            description='3',
            id_str=topic_id,
            overwrite=True)

        topics = self.C.get_topics()
        self.assertEqual(len(topics), 1)
        self.assertEqual(topics[0]["id"], topic_id)
        self.assertEqual(topics[0]["description"], "3")

    def test_template_topics(self):
        template_id = self.C.add_topic(
            "test_template",
            type_str='template',
            fields=['number'])
        self.assertEqual(template_id, "test_template")

        topic_id = self.C.add_topic('topic', template=template_id)
        topic_d = self.C.get_topic(topic_id)
        self.assertEqual(topic_d.get('fields'), ['number'])

        topics = self.C.get_topics()
        self.assertEqual(len(topics), 2)
        for topic in topics:
            self.assertEqual(topic.get('fields'), ['number'])

    def test_cannot_add_topic_with_invalid_template(self):
        with self.assertRaises(KeyError):
            self.C.add_topic('topic1', template='test_template')

        self.C.add_topic("test_template", type_str='template')
        topic_id = self.C.add_topic('topic2', template='test_template')

        with self.assertRaises(AssertionError):
            self.C.add_topic('topic3', template=topic_id)

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

    def test_cannot_add_data_to_template(self):
        topic_id = self.C.add_topic(
            "topic",
            type_str="template",
            fields=["number"])
        with self.assertRaises(AssertionError):
            self.C.add_data(topic_id, {"number": 3})

    def test_add_data_affects_get_data_output(self):
        topic_id = self.C.add_topic(
            "topic",
            description="description",
            fields=["number"])
        timestamp = self.C.add_data(topic_id, {"number": 3})
        self.assertIsNotNone(timestamp)
        self.assertEqual(self.C.get_data(topic_id)[0]["number"], 3)
        self.assertEqual(len(self.C.get_data(topic_id)), 1)

    def test_cannot_add_duplicate_timestamp_unless_overwrite(self):
        topic_id = self.C.add_topic(
            "topic",
            description="description",
            fields=["number"])
        timestamp = datetime(2020, 1, 1, 1, 0)
        created = self.C.add_data(topic_id, {
            "number": 3,
            "timestamp": timestamp})

        self.assertEqual(created, f'{timestamp.isoformat()}Z')

        with self.assertRaises(AssertionError):
            self.C.add_data(topic_id, {
                "number": 5,
                "timestamp": timestamp})

        self.C.add_data(topic_id, {
            "number": 7,
            "timestamp": timestamp}, overwrite=True)

        data = self.C.get_data(topic_id)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["number"], 7)

    def test_cannot_get_undefined_topic(self):
        with self.assertRaises(KeyError):
            self.C.get_topic("topic_id")

    def test_cannot_get_data_of_undefined_topic(self):
        with self.assertRaises(KeyError):
            self.C.get_data("topic_id")

    def _create_data_for_filter_test(self):
        topic_id = self.C.add_topic(
            "topic",
            description="description",
            data_tools=[dict(method="line", field="number")],
            fields=["number"])

        for i in range(10):
            with freeze_time(datetime(2020, 1, 1, 1, i)):
                self.C.add_data(topic_id, {"number": 3})

        return topic_id

    def test_can_get_data_since(self):
        topic_id = self._create_data_for_filter_test()

        data = self.C.get_data(topic_id, since=datetime(2020, 1, 1, 1, 5))
        self.assertEqual(data[0].get('timestamp'), '2020-01-01T01:05:00Z')
        self.assertEqual(len(data), 5)

    def test_can_get_data_until(self):
        topic_id = self._create_data_for_filter_test()

        data = self.C.get_data(topic_id, until=datetime(2020, 1, 1, 1, 5))
        self.assertEqual(data[0].get('timestamp'), '2020-01-01T01:00:00Z')
        self.assertEqual(data[-1].get('timestamp'), '2020-01-01T01:05:00Z')
        self.assertEqual(len(data), 6)

    def test_can_get_data_limit(self):
        topic_id = self._create_data_for_filter_test()

        data = self.C.get_data(topic_id, limit=5)
        self.assertEqual(data[0].get('timestamp'), '2020-01-01T01:05:00Z')
        self.assertEqual(len(data), 5)

    def test_can_get_summary_since_until_limit(self):
        topic_id = self._create_data_for_filter_test()

        data = self.C.get_summary(
            topic_id, since=datetime(
                2020, 1, 1, 1, 5), until=datetime(
                2020, 1, 1, 1, 7), limit=2)
        dataset = data["statistics"][0]["payload"]["data"]["datasets"][0]
        self.assertEqual(len(dataset["data"]), 2)
        self.assertEqual(dataset["data"][0]["x"], '2020-01-01T01:06:00Z')

    def test_can_get_overview_since_until_limit(self):
        topic_id = self._create_data_for_filter_test()

        data = self.C.get_overview(
            since=datetime(
                2020, 1, 1, 1, 3), until=datetime(
                2020, 1, 1, 1, 7), limit=10)
        dataset = data["statistics"][0]["payload"]["data"]["datasets"][0]
        self.assertEqual(len(dataset["data"]), 5)
        self.assertEqual(dataset["data"][0]["x"], '2020-01-01T01:03:00Z')
        self.assertEqual(dataset["data"][-1]["x"], '2020-01-01T01:07:00Z')

    def test_can_get_topics_type_and_template(self):
        self.C.add_topic(
            "te1",
            type_str="template",
            fields=["number"])
        self.C.add_topic(
            "te2",
            type_str="template",
            fields=["letter"])
        self.C.add_topic(
            "1",
            template="te1")
        self.C.add_topic(
            "2",
            template="te1")
        self.C.add_topic(
            "3",
            template="te2")

        topics = self.C.get_topics('template')
        self.assertEqual(len(topics), 2)

        topics = self.C.get_topics('topic')
        self.assertEqual(len(topics), 3)

        topics = self.C.get_topics(template='te1')
        self.assertEqual(len(topics), 2)

        topics = self.C.get_topics(template='te2')
        self.assertEqual(len(topics), 1)
