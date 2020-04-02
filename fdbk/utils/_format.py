from datetime import datetime
from uuid import uuid4

from fdbk.validate import validate_topic_dict

TOPIC_FIELDS = [
    "name",
    "id",
    "type",
    "description",
    "fields",
    "units",
    "data_tools",
    "metadata",
]


def timestamp_as_str(timestamp):
    return f"{timestamp.isoformat()}Z"


def generate_data_entry(topic_id, fields, values, convert_timestamps=False):
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

    timestamp = datetime.utcnow()
    if convert_timestamps:
        timestamp = timestamp_as_str(timestamp)

    data = {
        "topic_id": topic_id,
        "timestamp": timestamp
    }
    for field in fields:
        if field not in values.keys():
            raise ValueError("Value for field '" + field +
                             "' not present in input data")
        data[field] = values[field]

    return data


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
            "timestamp": timestamp_as_str(d["timestamp"])
        })
        for field in fields:
            ret[-1][field] = d[field]
    return ret


def generate_topic_dict(
        name,
        type_str=None,
        description=None,
        fields=None,
        units=None,
        data_tools=None,
        metadata=None,
        add_id=True):
    '''Generate topic dictionary

    Args:
        name: Name of the topic.
        type_str: Type of the topic, for example 'form' or 'sensor'.
        description: Description of the topic.
        fields: List of data field names included in the topic.
        units: List of units for field.
        data_tools: List of data_tools instructions for corresponding
            fields.
        metadata: Dict of metadata for topic
        add_id: Boolean to tell if id should be added

    Returns:
        Generated topic dict

    '''
    topic_d = {
        "name": name,
        "type": type_str,
        "description": description,
        "fields": fields if fields is not None else [],
        "units": units if units is not None else [],
        "data_tools": data_tools if data_tools is not None else [],
        "metadata": metadata if metadata is not None else {},
    }

    if add_id:
        topic_d["id"] = str(uuid4())

    validate_topic_dict(topic_d)

    return topic_d


def generate_topic_response(topic):
    ''' Removes DB specific fields from the topic data

    Args:
        topics: DB entry

    Returns:
        Standardized topic dict
    '''
    topic_d = {}
    for field in TOPIC_FIELDS:
        topic_d[field] = topic[field]
    return topic_d


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
            generate_topic_response(topic)
        )
    return ret
