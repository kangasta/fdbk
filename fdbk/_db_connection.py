'''Base class for DB connections.
'''

from concurrent.futures import wait, ALL_COMPLETED, ThreadPoolExecutor

from fdbk.data_tools import combine_run_outputs, post_process, run_data_tools
from fdbk.utils.messages import topic_not_found


class DBConnection:
    '''Base class for DB connections.
    '''

    def validate_template(self, topic_d):
        ''' Validate that topics template is a template topic

        Args:
            topic_d: Topic dict which template is validated

        Returns:
            None

        Raises:
            AssertionError: Template is not a valid template
            KeyError: Template not found from DB
        '''
        template = topic_d.get('template')
        if not template:
            return

        template_d = self.get_topic(template)
        if template_d.get('type') != 'template':
            raise AssertionError('Templates type is not template.')

    def add_topic(self, name, overwrite=False, **kwargs):
        '''Adds new topic to DB.

        Args:
            name: Name of the topic.
            overwrite: Boolean to enable overwriting existing topic with the
                same id. Disabled by default.
            kwargs: See fdbk.utils.generate_topic_dict

        Returns:
            Topic ID of the newly created topic

        Raises:
            KeyError: Topic already exists in DB or topics template does not
                exist in DB.
        '''
        raise NotImplementedError(
            "Functionality not implemented by selected DB connection")

    def add_data(self, topic_id, values, overwrite=False):
        '''Adds data under given topic in DB

        Args:
            topic_id: ID of the topic under which to add data.
            values: Dictionary with field names as keys and field value as
                value.
            overwrite: Boolean to enable overwriting existing data-point with
                the same topic id and timestamp. Disabled by default.

        Returns:
            timestamp of the created data point as ISO 8601 string

        Raises:
            AssertionError: Topic is a template topic, topic already has data
                for given timestamp.
            KeyError: Topic does not exist in DB
            ValueError: Values do not match those defined for the topic
        '''
        raise NotImplementedError(
            "Functionality not implemented by selected DB connection")

    def get_topics_without_templates(self, type_=None, template=None):
        '''Gets list of topic dicts without resolving templates

        Fetches all topics by default.

        Args:
            type_: Type of topics to fetch
            template: Template of topics to fetch.

        Returns:
            List of topic dicts without fields from possible templates
        '''
        raise NotImplementedError(
            "Functionality not implemented by selected DB connection")

    @staticmethod
    def _remove_empty(obj):
        ret = {}
        for key, value in obj.items():
            if value:
                ret[key] = value
        return ret

    @staticmethod
    def _with_templates(topic_d, templates):
        template = topic_d.get('template')
        if template:
            try:
                template_d = next(
                    i for i in templates if i.get('id') == template)
            except StopIteration:
                raise KeyError(topic_not_found(template))
            return {
                **DBConnection._with_templates(
                    template_d,
                    templates),
                **DBConnection._remove_empty(topic_d)}
        else:
            return topic_d

    def get_topics(self, type_=None, template=None):
        '''Gets list of topic dicts with values from templates

        Fetches all topics by default.

        Args:
            type_: Type of topics to fetch
            template: Template of topics to fetch.

        Returns:
            List of topic dicts

        Raises:
            KeyError: Template of a topic not found from the DB
        '''
        topics = self.get_topics_without_templates(type_, template=template)
        templates = self.get_topics_without_templates(type_='template')

        return [self._with_templates(topic, templates) for topic in topics]

    def get_topic_without_templates(self, topic_id):
        '''Get topic dict by ID without resolving templates

        Args:
            topic_id: ID of the topic to find

        Returns:
            Topic dictionary without fields from possible templates

        Raises:
            KeyError: Topic does not exist in DB
        '''
        raise NotImplementedError(
            "Functionality not implemented by selected DB connection")

    def get_topic(self, topic_id):
        '''Get topic dict by ID with values from templates

        Args:
            topic_id: ID of the topic to find

        Returns:
            Topic dictionary with matching name

        Raises:
            KeyError: Topic does not exist in DB
        '''
        topic_d = self.get_topic_without_templates(topic_id)
        template = topic_d.get('template')
        if template:
            return {**self.get_topic(template), **self._remove_empty(topic_d)}
        else:
            return topic_d

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
            aggregate_with=None,
            aggregate_always=False):
        '''Get summary of the topic data

        Args:
            topic_id: ID of the topic to get the summary of
            since: Datetime of the earliest entry to include
            until: Datetime of the most recent entry to include
            limit: Number of entries to include from the most recent
            aggregate_to: Aggregate data into specified number of data points
            aggregate_with: Aggregate data with speficied function
            aggregate_always: Aggregate data even if datas length is
                shorter than aggregate_to value. Disabled by default.

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
            topic_d, data_d, aggregate_to, aggregate_with, aggregate_always,)
        summary_d["warnings"].extend(warnings)

        results, warnings = post_process(results)
        summary_d["statistics"] = results
        summary_d["warnings"].extend(warnings)

        return summary_d

    def _get_topic_statistics(
            self,
            topic_d,
            since=None,
            until=None,
            limit=None,
            aggregate_to=None,
            aggregate_with=None,
            aggregate_always=False):
        data_d = self.get_data(topic_d.get("id"), since, until, limit)
        return run_data_tools(
            topic_d,
            data_d,
            aggregate_to,
            aggregate_with,
            aggregate_always)

    def _run_data_tools_for_many(self,
                                 topic_ids=None,
                                 template=None,
                                 since=None,
                                 until=None,
                                 limit=None,
                                 aggregate_to=None,
                                 aggregate_with=None,
                                 aggregate_always=False):
        executor = ThreadPoolExecutor()
        warnings = []

        if topic_ids:
            topics = {}
            for topic_id in topic_ids:
                try:
                    topics[topic_id] = self.get_topic(topic_id)
                except KeyError as e:
                    warnings.append(topic_not_found(topic_id))
        else:
            topics = {
                topic["id"]: topic for topic in self.get_topics(template)}

        result_d = {
            "topic_names": [],
            "topic_ids": list(topics.keys()),
            "fields": [],
            "statistics": [],
            "warnings": warnings
        }

        jobs = []
        params = (
            since,
            until,
            limit,
            aggregate_to,
            aggregate_with,
            aggregate_always,
        )
        for topic_d in topics.values():
            if topic_d["type"] == "template":
                continue

            jobs.append(
                executor.submit(
                    self._get_topic_statistics, topic_d, *params))

            result_d["topic_names"].append(topic_d["name"])
            result_d["fields"].extend(topic_d["fields"])

        wait(jobs, return_when=ALL_COMPLETED)

        results, warnings = combine_run_outputs(job.result() for job in jobs)
        result_d["statistics"] = results
        result_d["warnings"].extend(warnings)

        result_d["fields"] = list(set(result_d["fields"]))
        return result_d

    def get_overview(
            self,
            topic_ids=None,
            template=None,
            since=None,
            until=None,
            limit=None,
            aggregate_to=None,
            aggregate_with=None,
            aggregate_always=False):
        '''Get overview of the data

        Args:
            topic_ids: List of topic IDs to overview. By default all topics are
                included.
            template: Template of topics to include. Only has effect if
                topic_ids is empty. By default all topics are included.
            since: Datetime of the earliest entry to include
            until: Datetime of the most recent entry to include
            limit: Number of entries to include from the most recent
            aggregate_to: Aggregate data into specified number of data points
            aggregate_with: Aggregate data with speficied function
            aggregate_always: Aggregate data even if datas length is
                shorter than aggregate_to value. Disabled by default.

        Returns:
            Dictionary with overview of the topics data

        Raises:
            KeyError: Topic does not exist in DB
        '''
        return self._run_data_tools_for_many(
            topic_ids=topic_ids,
            template=template,
            since=since,
            until=until,
            limit=limit,
            aggregate_to=aggregate_to,
            aggregate_with=aggregate_with,
            aggregate_always=aggregate_always)


ConnectionClass = DBConnection
