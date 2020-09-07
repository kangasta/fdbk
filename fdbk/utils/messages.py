def _topic_str(topic_d):
    type_ = topic_d.get("type") or topic_d.get("type_str", "topic")
    type_str = f', {type_}' if type_ != 'topic' else ''
    return f'{topic_d["name"]} ({topic_d["id"]}{type_str})'


def created_connection(plugin, parameters):
    return (
        f"Created fdbk DB connection of type '{plugin}' with parameters "
        f"{str(parameters)}.")


def created_topic(topic_d, id_):
    topic_d = {**topic_d, "id": id_}
    return (f"Created topic '{_topic_str(topic_d)}' to the database.")


def collection_name_is_undefined(method, field):
    return f'No target list name specified for {method} {field}.'


def field_is_undefined(field):
    return f'The requested field "{field}" is undefined.'


def method_not_supported(method):
    return f'The requested method "{method}" is not supported.'


def no_data(topic_d=None):
    if topic_d:
        topic_details = f' for topic {_topic_str(topic_d)}'
    else:
        topic_details = ''
    return f'No data found{topic_details}.'


def topic_not_found(id_):
    return f'Topic ID "{id_}" not found from database.'


def duplicate_timestamp(topic_d, timestamp):
    return (
        f'Topic {_topic_str(topic_d)} already has data for given timestamp '
        f'({timestamp}).'
    )


def duplicate_topic_id(id_):
    return (
        f'Topic ID "{id_}" already found from the database.'
    )
