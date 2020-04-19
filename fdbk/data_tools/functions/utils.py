def statistics_dict(type_, metadata=None, parameters=None, **kwargs):
    statistic_d = dict(type=type_, payload=kwargs)
    if metadata:
        statistic_d["metadata"] = metadata
    if parameters:
        statistic_d["parameters"] = parameters

    return statistic_d


def chart_dict(**kwargs):
    return statistics_dict("chart", **kwargs)


def value_dict(**kwargs):
    return statistics_dict("value", **kwargs)
