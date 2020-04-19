def _statistics_dict(type_, metadata=None, **kwargs):
    statistic_d = dict(type=type_, payload=kwargs)
    if metadata:
        statistic_d["metadata"] = metadata

    return statistic_d


def chart_dict(**kwargs):
    return _statistics_dict("chart", **kwargs)


def value_dict(metadata=None, **kwargs):
    return _statistics_dict("value", **kwargs)
