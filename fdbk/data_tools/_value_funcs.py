from numbers import Number

from ._utils import _value_dict


def average(data, field):
    filtered_data = [d[field]
                     for d in data if isinstance(d[field], Number)]
    if not filtered_data:
        return None

    return _value_dict(
        type="average",
        field=field,
        value=sum(i / float(len(filtered_data)) for i in filtered_data)
    )


def latest(data, field):
    if not data:
        return None

    return _value_dict(
        type="latest",
        field=field,
        value=data[-1][field] if data else None
    )


def last(truthy_or_falsy, data, field):
    truthy_or_falsy = bool(truthy_or_falsy)
    filtered_data = [d for d in data if bool(d[field]) == truthy_or_falsy]
    if not filtered_data:
        return None

    type_str = "last_truthy" if truthy_or_falsy else "last_falsy"
    value = filtered_data[-1]["timestamp"]

    return _value_dict(
        type=type_str,
        field=field,
        value=value
    )


def last_truthy(data, field):
    return last(True, data, field)


def last_falsy(data, field):
    return last(False, data, field)


VALUE_FUNCS = dict(
    average=average,
    latest=latest,
    last_truthy=last_truthy,
    last_falsy=last_falsy,
)
