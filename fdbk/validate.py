'''Validation tools for input and output data
'''

import json
from jsonschema import validate

try:
    import importlib.resources as resources
except ImportError:  # pragma: no cover
    import importlib_resources as resources


def _validate_dict(input_dict, schema_name):
    schema = json.loads(
        resources.read_text(
            'fdbk.schemas',
            f'{schema_name}.json'))
    validate(instance=input_dict, schema=schema)


def validate_topic_dict(topic_d):
    '''Validate topic when creating or modifying topics
    '''
    _validate_dict(topic_d, 'topic-in')


def validate_statistics_array(statistics):
    '''Validate output statistics array
    '''
    _validate_dict(statistics, 'statistics-out')
