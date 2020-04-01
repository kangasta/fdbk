'''Utilities for users
'''

from argparse import ArgumentParser
from datetime import datetime
from importlib import import_module
from uuid import uuid4

from fdbk.validate import validate_topic_dict

BUILT_IN = dict(
    client="fdbk._client_connection",
    ClientConnection="fdbk._client_connection",
    dict="fdbk._dict_connection",
    DictConnection="fdbk._dict_connection",
)


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


def create_db_connection(db_plugin, db_parameters):
    if db_plugin in BUILT_IN.keys():
        db_plugin = BUILT_IN.get(db_plugin)

    try:
        db_connection_mod = import_module(db_plugin)
        return db_connection_mod.ConnectionClass(*db_parameters)
    except Exception as e:
        raise RuntimeError(
            "Loading or creating fdbk DB connection failed: " + str(e))


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


def generate_topic_dict(
        name,
        type_str="",
        description="",
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


def get_reporter_argparser(parser=None):
    if not parser:
        parser = ArgumentParser()

    parser.add_argument(
        "db_parameters",
        nargs="+",
        type=str,
        help="Parameters for fdbk DB connection.")
    parser.add_argument(
        "--db-connection",
        type=str,
        default="ClientConnection",
        help="fdbk DB connection to use (default=ClientConnection)")
    parser.add_argument(
        "--interval",
        "-i",
        type=float,
        default=360.0,
        help="Data pushing interval in seconds.")
    parser.add_argument(
        "--num-samples",
        "-n",
        type=int,
        default=60,
        help="Number of samples to average during the push interval")
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print progress messages")

    return parser
