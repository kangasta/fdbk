'''Base class for DB connections.
'''

from fdbk.data_tools import post_process, run_data_tools


class DBConnection:
    '''Base class for DB connections.
    '''

    def add_topic(self, name, **kwargs):
        '''Adds new topic to DB.

        Args:
            name: Name of the topic.

        Returns:
            Topic ID of the newly created topic

        Raises:
            KeyError: Topic already exists in DB
        '''
        raise NotImplementedError(
            "Functionality not implemented by selected DB connection")

    def add_data(self, topic_id, values):
        '''Adds data under given topic in DB

        Args:
            topic_id: ID of the topic under which to add data.
            values: Dictionary with field names as keys and field value as
                value.

        Returns:
            None

        Raises:
            KeyError: Topic does not exist in DB
            ValueError: Values do not match those defined for the topic
        '''
        raise NotImplementedError(
            "Functionality not implemented by selected DB connection")

    def get_topics(self, type_=None):
        '''Gets list of topic dicts

        Args:
            type_: Type of topics to fetch. By default all topics are fetched.

        Returns:
            List of topic dicts
        '''
        raise NotImplementedError(
            "Functionality not implemented by selected DB connection")

    def get_topic(self, topic_id):
        '''Get topic dict by ID

        Args:
            topic_id: ID of the topic to find

        Returns:
            Topic dictionary with matching name

        Raises:
            KeyError: Topic does not exist in DB
        '''
        raise NotImplementedError(
            "Functionality not implemented by selected DB connection")

    def get_data(self, topic_id, since=None, until=None, limit=None):
        '''Get all data under given topic

        Args:
            topic_id: ID of the topic to find
            since: Datetime of the earliest entry to include
            until: Datetime of the most recent entry to include
            limit: Number of entries to include from the most recent

        Returns:
            List of all data dicts under topic with matching name

        Raises:
            KeyError: Topic does not exist in DB
        '''
        raise NotImplementedError(
            "Functionality not implemented by selected DB connection")

    def get_latest(self, topic_id):
        '''Get latest data element of given topic

        Note that this is an unoptimized implementation that wont be efficient
        for most databases. This method should be overridden by inheriting
        classes.

        Args:
            topic_id: ID of the topic to find

        Returns:
            Latest data dict under topic with matching name

        Raises:
            KeyError: Topic does not exist in DB
            IndexError: Topic has no data available

        '''
        return self.get_data(topic_id)[-1]

    def get_summary(
            self,
            topic_id,
            since=None,
            until=None,
            limit=None,
            aggregate_to=None,
            aggregate_with=None):
        '''Get summary of the topic data

        Args:
            topic_id: ID of the topic to get the summary of
            since: Datetime of the earliest entry to include
            until: Datetime of the most recent entry to include
            limit: Number of entries to include from the most recent
            aggregate_to: Aggregate data into specified number of data points
            aggregate_with: Aggregate data with speficied function

        Returns:
            Dictionary with summary of the topic

        Raises:
            KeyError: Topic does not exist in DB
        '''
        data_d = self.get_data(topic_id, since, until, limit)
        topic_d = self.get_topic(topic_id)

        summary_d = {
            "topic": topic_d["name"],
            "description": topic_d["description"],
            "units": topic_d["units"],
            "num_entries": len(data_d),
            "statistics": [],
            "warnings": []
        }

        results, warnings = run_data_tools(
            topic_d, data_d, aggregate_to, aggregate_with)
        summary_d["warnings"].extend(warnings)

        results, warnings = post_process(results)
        summary_d["statistics"] = results
        summary_d["warnings"].extend(warnings)

        return summary_d

    def _run_data_tools_for_many(self,
                                 topic_ids=None,
                                 type_=None,
                                 since=None,
                                 until=None,
                                 limit=None,
                                 aggregate_to=None,
                                 aggregate_with=None):
        if not topic_ids:
            # TODO: only fetch topics list once in this function
            topic_ids = [topic["id"] for topic in self.get_topics(type_)]

        result_d = {
            "topic_names": [],
            "topic_ids": topic_ids,
            "fields": [],
            "statistics": [],
            "warnings": []
        }

        results = []
        for topic_id in topic_ids:
            data_d = self.get_data(topic_id, since, until, limit)
            topic_d = self.get_topic(topic_id)

            result_d["topic_names"].append(topic_d["name"])
            result_d["fields"].extend(topic_d["fields"])

            new_results, warnings = run_data_tools(
                topic_d, data_d, aggregate_to, aggregate_with)
            results.extend(new_results)
            result_d["warnings"].extend(warnings)

        results, warnings = post_process(results)
        result_d["statistics"] = results
        result_d["warnings"].extend(warnings)

        result_d["fields"] = list(set(result_d["fields"]))
        return result_d

    def get_comparison(self, topic_ids=None, **kwargs):
        '''Get comparison of the data of the given topic IDs

        See get_overview.
        '''
        return self._run_data_tools_for_many(topic_ids, **kwargs)

    def get_overview(
            self,
            topic_ids=None,
            type_=None,
            since=None,
            until=None,
            limit=None,
            aggregate_to=None,
            aggregate_with=None):
        '''Get overview of the data

        Args:
            topic_ids: List of topic IDs to overview. By default all topics are
                included.
            type_: Type of topics to include. Only has effect is topic_ids is
                empty. By default all topics are included.
            since: Datetime of the earliest entry to include
            until: Datetime of the most recent entry to include
            limit: Number of entries to include from the most recent
            aggregate_to: Aggregate data into specified number of data points
            aggregate_with: Aggregate data with speficied function

        Returns:
            Dictionary with overview of the topics data

        Raises:
            KeyError: Topic does not exist in DB
        '''
        return self._run_data_tools_for_many(
            topic_ids=topic_ids,
            type_=type_,
            since=since,
            until=until,
            limit=limit,
            aggregate_to=aggregate_to,
            aggregate_with=aggregate_with)


ConnectionClass = DBConnection
