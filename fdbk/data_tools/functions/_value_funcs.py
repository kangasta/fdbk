from numbers import Number
from statistics import mean, median

from .utils import value_dict


def use_function(function, name, check_empty=False):
    def value_function(data, field, parameters=None):
        try:
            if check_empty:
                next(d[field] for d in data if isinstance(d[field], Number))

            return value_dict(
                type=name, field=field, value=function(
                    d[field] for d in data if isinstance(
                        d[field], Number)))
        except Exception:
            return None

    return value_function


def latest(data, field, parameters=None):
    if not data:
        return None

    return value_dict(
        type="latest",
        field=field,
        value=data[-1][field] if data else None
    )


def last(truthy_or_falsy, data, field, parameters=None):
    truthy_or_falsy = bool(truthy_or_falsy)
    filtered_data = [d for d in data if bool(d[field]) == truthy_or_falsy]
    if not filtered_data:
        return None

    type_str = "last_truthy" if truthy_or_falsy else "last_falsy"
    value = filtered_data[-1]["timestamp"]

    return value_dict(
        type=type_str,
        field=field,
        value=value
    )


def last_truthy(data, field, parameters=None):
    return last(True, data, field)


def last_falsy(data, field, parameters=None):
    return last(False, data, field)


VALUE_FUNCS = dict(
    average=use_function(mean, 'average'),
    max=use_function(max, 'max'),
    mean=use_function(mean, 'mean'),
    median=use_function(median, 'median'),
    min=use_function(min, 'min'),
    latest=latest,
    last_truthy=last_truthy,
    last_falsy=last_falsy,
    sum=use_function(sum, 'sum', check_empty=True),
)
