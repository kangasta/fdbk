from datetime import datetime
from uuid import uuid4

from fdbk.data_tools import SummaryFuncs, VisualizationFuncs


class DBConnection:
    '''Base class for DB connections.
    '''

    TOPIC_FIELDS = [
        "name",
        "id",
        "type",
        "description",
        "fields",
        "units",
        "summary",
        "visualization",
        "metadata",
        "form_submissions"
    ]

    @staticmethod
    def generate_topic_dict(
            name,
            type_str="",
            description="",
            fields=None,
            units=None,
            summary=None,
            visualization=None,
            metadata=None,
            form_submissions=False,
            add_id=True):
        '''Generate topic dictionary

        Args:
            name: Name of the topic.
            type_str: Type of the topic, for example 'form' or 'sensor'.
            description: Description of the topic.
            fields: List of data field names included in the topic.
            units: List of units for field.
            summary: List of summary instructions for corresponding fields.
            visualization: List of visualization instructions for corresponding
                fields.
            metadata: Dict of metadata for topic
            form_submissions: Boolean to determine if data for this topic
                should be added through the API

        Returns:
            Generated topic dict

        '''
        topic_d = {
            "name": name,
            "type": type_str,
            "description": description,
            "fields": fields if fields is not None else [],
            "units": units if units is not None else [],
            "summary": summary if summary is not None else [],
            "visualization": (
                visualization if visualization is not None else []
            ),
            "metadata": metadata if metadata is not None else {},
            "form_submissions": form_submissions}

        if add_id:
            topic_d["id"] = str(uuid4())

        return topic_d

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

    @staticmethod
    def generate_data_entry(topic_id, fields, values):
        '''Generates data entry to add to the DB

        Validates that the fields match to the ones specified by the provided
        topic ID. Adds topic ID and timestamp to the provides values entry.

        Args:
            topic_id: Topic ID to add to the entry
            fields: Fields to validate against
            values: Valued to add to the data entry

        Returns:
            Data entry dict with timestamp and topic ID

        Raises:
            ValueError: provided values do not match to the provided fields
        '''
        if len(fields) != len(values):
            raise ValueError(
                "The number of given values does not match with "
                "the number of fields defined for topic"
            )

        data = {
            "topic_id": topic_id,
            "timestamp": datetime.utcnow()
        }
        for field in fields:
            if field not in values.keys():
                raise ValueError("Value for field '" + field +
                                 "' not present in input data")
            data[field] = values[field]

        return data

    def get_topics(self):
        '''Gets list of topic dicts

        Returns:
            List of topic dicts
        '''
        raise NotImplementedError(
            "Functionality not implemented by selected DB connection")

    @staticmethod
    def generate_topics_list(topics):
        ''' Removes DB specific fields from the topics list

        Args:
            topics: List of DB entries

        Returns:
            Standardized topics list
        '''
        ret = []
        for topic in topics:
            ret.append(
                DBConnection.generate_topic_response(topic)
            )
        return ret

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

    @staticmethod
    def generate_topic_response(topic):
        ''' Removes DB specific fields from the topic data

        Args:
            topics: DB entry

        Returns:
            Standardized topic dict
        '''
        topic_d = {}
        for field in DBConnection.TOPIC_FIELDS:
            topic_d[field] = topic[field]
        return topic_d

    def get_data(self, topic_id):
        '''Get all data under given topic

        Args:
            topic_id: ID of the topic to find

        Returns:
            List of all data dicts under topic with matching name

        Raises:
            KeyError: Topic does not exist in DB
        '''
        raise NotImplementedError(
            "Functionality not implemented by selected DB connection")

    @staticmethod
    def generate_data_response(data, fields):
        ''' Generate standardized data list from DB entries

        Standardizes the DB entries from the DB and converts the timestamps to
        ISO 8601 strings.

        Args:
            data: List of DB data entries
            fields: Fields to parse from DB data entries

        Returns:
            Standardized data list
        '''
        ret = []
        for d in data:
            ret.append({
                "topic_id": d["topic_id"],
                "timestamp": d["timestamp"].isoformat() + "Z"
            })
            for field in fields:
                ret[-1][field] = d[field]
        return ret

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

    def _run_data_tools(self, key, topic_d, data):
        if key == "summary":
            funcs = SummaryFuncs()
        elif key == "visualization":
            funcs = VisualizationFuncs()
        else:
            raise ValueError("Data tools target '" +
                             str(key) + "' not supported.")

        results = []
        warnings = []

        for instruction in topic_d[key]:
            if instruction["method"] not in funcs:
                warnings.append("The requested method '" +
                                instruction["method"] + "' is not supported.")
                continue
            if instruction["field"] not in topic_d["fields"]:
                warnings.append("The requested field '" +
                                instruction["field"] + "' is undefined.")
                continue

            result = funcs[instruction["method"]](
                data, instruction["field"]
            )
            if result is not None:
                result["topic_name"] = topic_d["name"]
                try:
                    result["unit"] = next(
                        i["unit"] for i in topic_d["units"] if (
                            i["field"] == instruction["field"])
                    )
                except StopIteration:
                    result["unit"] = None

            results.append(result)

        return (results, warnings,)

    def get_summary(self, topic_id):
        '''Get summary of the topic data

        Args:
            topic_id: ID of the topic to get the summary of

        Returns:
            Dictionary with summary of the topic

        Raises:
            KeyError: Topic does not exist in DB
        '''
        data_d = self.get_data(topic_id)
        topic_d = self.get_topic(topic_id)

        summary_d = {
            "topic": topic_d["name"],
            "description": topic_d["description"],
            "units": topic_d["units"],
            "num_entries": len(data_d),
            "summaries": [],
            "visualizations": [],
            "warnings": []
        }

        results, warnings = self._run_data_tools("summary", topic_d, data_d)
        summary_d["summaries"].extend(results)
        summary_d["warnings"].extend(warnings)

        results, warnings = self._run_data_tools(
            "visualization", topic_d, data_d)
        summary_d["visualizations"].extend(results)
        summary_d["warnings"].extend(warnings)

        return summary_d

    def _run_data_tools_for_many(self, key=None, topic_ids=None):
        if key == "summary":
            result_key = "summaries"
        elif key == "visualization":
            result_key = "visualizations"
        else:
            raise ValueError("Data tools target '" +
                             str(key) + "' not supported.")

        if topic_ids is None:
            topic_ids = [topic["id"] for topic in self.get_topics()]

        result_d = {
            "topic_names": [],
            "topic_ids": topic_ids,
            "fields": [],
            result_key: [],
            "warnings": []
        }

        for topic_id in topic_ids:
            data_d = self.get_data(topic_id)
            topic_d = self.get_topic(topic_id)

            result_d["topic_names"].append(topic_d["name"])
            result_d["fields"].extend(topic_d["fields"])

            results, warnings = self._run_data_tools(key, topic_d, data_d)
            result_d[result_key].extend(results)
            result_d["warnings"].extend(warnings)

        result_d["fields"] = list(set(result_d["fields"]))
        return result_d

    def get_comparison(self, topic_ids):
        '''Get comparison of the data of the given topic IDs

        Args:
            topic_ids: List of topic IDs to compare

        Returns:
            Dictionary with comparison of the topics data

        Raises:
            KeyError: Topic does not exist in DB
        '''
        return self._run_data_tools_for_many(
            key="visualization", topic_ids=topic_ids)

    def get_overview(self, topic_ids=None):
        '''Get overview of the data

        Args:
            topic_ids: List of topic IDs to overview. If not given, overview
            of all topics is generated.

        Returns:
            Dictionary with overview of the topics data

        Raises:
            KeyError: Topic does not exist in DB
        '''
        return self._run_data_tools_for_many(
            key="summary", topic_ids=topic_ids)


ConnectionClass = DBConnection
