def collection_name_is_undefined(method, field):
    return f'No target list name specified for {method} {field}.'


def field_is_undefined(field):
    return f'The requested field "{field}" is undefined.'


def method_not_supported(method):
    return f'The requested method "{method}" is not supported.'


def no_data(topic_d=None):
    if topic_d:
        topic_details = f' for topic {topic_d["name"]} ({topic_d["id"]})'
    else:
        topic_details = ''
    return f'No data found{topic_details}.'


def topic_not_found(id_):
    return f'Topic ID "{id_}" not found from database'
