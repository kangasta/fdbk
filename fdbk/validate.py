import json
from jsonschema import validate

try:
    import importlib.resources as resources
except ImportError:  # pragma: no cover
    import importlib_resources as resources


def validate_dict(input_dict, schema_name):
    schema = json.loads(
        resources.read_text(
            'fdbk.schemas',
            f'{schema_name}.json'))
    validate(instance=input_dict, schema=schema)


def validate_topic_dict(topic_d):
    validate_dict(topic_d, 'topic-in')
