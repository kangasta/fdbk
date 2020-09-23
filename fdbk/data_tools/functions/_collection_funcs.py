from fdbk.utils.messages import method_not_supported

from .utils import statistics_dict
from ._chart_funcs import CHART_FUNCS
from ._status_funcs import STATUS_FUNCS
from ._value_funcs import VALUE_FUNCS


def _collection(type_, data, field, parameters=None):
    try:
        method = parameters.get("method", "latest")
        child_parameters = parameters.get("parameters")
    except AttributeError:
        return None

    functions = {**CHART_FUNCS, **STATUS_FUNCS, **VALUE_FUNCS}
    if method not in functions:
        raise ValueError(method_not_supported(method))

    value_d = functions.get(method)(data, field, child_parameters)
    return statistics_dict(type_, parameters=parameters, **value_d)


def table_item(data, field, parameters=None):
    return _collection("table_item", data, field, parameters)


def list_item(data, field, parameters=None):
    return _collection("list_item", data, field, parameters)


COLLECTION_FUNCS = dict(
    list_item=list_item,
    table_item=table_item,
)
