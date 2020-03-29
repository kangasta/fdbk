def _statistics_dict(type_, **kwargs):
    return dict(type=type_, payload=kwargs)


def _chart_dict(**kwargs):
    return _statistics_dict("chart", **kwargs)


def _value_dict(**kwargs):
    return _statistics_dict("value", **kwargs)


def _create_chart(type_, field):
    return dict(
        field=field,
        type=type_,
        data=dict(datasets=[], labels=[]),
    )


def _visualization_to_dataset(visualization):
    return dict(
        data=visualization.get('data'),
        label=visualization.get('topic_name')
    )


def process_charts(statistics):
    charts = {}
    other = []

    for i in statistics:
        if not i:
            continue
        if i.get("type") != "chart":
            other.append(i)
            continue

        i = i.get('payload')

        field = i.get('field')
        type_ = i.get('type')
        key = f"{field}-{type_}"

        if key not in charts:
            charts[key] = _create_chart(type_, field)

        charts[key]['data']['labels'] = (
            list(set(charts[key]['data']['labels'] + i.get("labels", []))))
        charts[key]["data"]['datasets'].append(_visualization_to_dataset(i))

    return list(_chart_dict(**chart) for chart in charts.values()) + other


def post_process(statistics):
    return process_charts(statistics)
