from datetime import timezone
from dateutil.parser import isoparse

from fdbk.utils import timestamp_as_str
from fdbk.utils.messages import (
    method_not_supported,
    no_data)

from .functions import functions as data_functions, VALUE_FUNCS


def _dt_timestamp(data_point):
    return isoparse(data_point.get('timestamp'))


def _as_naive_utc(dt_timestamp):
    return dt_timestamp.astimezone(timezone.utc).replace(tzinfo=None)


def _get_keys(data_point):
    return [key for key in data_point if key != 'timestamp']


def aggregate(data, aggregate_to, aggregate_with=None):
    if not aggregate_with:
        aggregate_with = 'average'

    warnings = []
    aggregated = []

    if not data:
        warnings.append(no_data())
        return ([], warnings,)

    if aggregate_with not in VALUE_FUNCS:
        warnings.append(method_not_supported(aggregate_with))
        return ([], warnings,)

    start = _dt_timestamp(data[0])
    end = _dt_timestamp(data[-1])
    window = (end - start) / aggregate_to

    keys = _get_keys(data[0])
    remaining = data
    for i in range(aggregate_to):
        try:
            last = next(j for j, a in enumerate(remaining)
                        if _dt_timestamp(a) > start + (i + 1) * window)
            current = remaining[:last]
            if not current:
                continue
            remaining = remaining[last:]
        except StopIteration:
            if i == (aggregate_to - 1):
                current = remaining
            else:
                continue

        aggregated_point = dict(
            timestamp=timestamp_as_str(
                _as_naive_utc(
                    start + i * window)))
        for key in keys:
            try:
                aggregated_point[key] = data_functions[aggregate_with](
                    current, key, None).get('payload').get('value')
            except BaseException:
                aggregated_point[key] = None
        aggregated.append(aggregated_point)

    return (aggregated, warnings,)
