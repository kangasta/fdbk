from .utils import statistics_dict
from ._value_funcs import VALUE_FUNCS as functions


def _collection(type_, data, field, parameters=None):
    try:
        method = parameters.get("method", "latest")
    except AttributeError:
        return None

    value_d = functions.get(method)(data, field, parameters)
    return statistics_dict(type_, parameters=parameters, **value_d)


def table_item(data, field, parameters=None):
    return _collection("table_item", data, field, parameters)


def list_item(data, field, parameters=None):
    return _collection("list_item", data, field, parameters)


COLLECTION_FUNCS = dict(
    list_item=list_item,
    table_item=table_item,
)
