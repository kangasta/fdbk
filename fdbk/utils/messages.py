def topic_not_found(id_):
    return f'Topic ID "{id_}" not found from database'


def method_not_supported(method):
    return f'The requested method "{method}" is not supported.'


def field_is_undefined(field):
    return f'The requested field "{field}" is undefined.'


def collection_name_is_undefined(method, field):
    return f'No target list name specified for {method} {field}.'
