from fdbk.utils.messages import collection_name_is_undefined

from .functions.utils import chart_dict, statistics_dict


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
    '''Combine charts of same field and type to single chart

    Args:
        statistics: Iterable of statistics

    Returns:
        List of statistics where charts with same field and type combined.
        Chart statistics are moved to the beginning of the list.
    '''
    charts = {}
    other = []

    for i in statistics:
        if not i:
            continue
        if i.get("type") != "chart":
            other.append(i)
            continue

        metadata = i.get("metadata")
        i = i.get('payload')

        field = i.get('field')
        type_ = i.get('type')
        key = f"{field}-{type_}"

        if key not in charts:
            charts[key] = _create_chart(type_, field)

        charts[key]['data']['labels'] = (
            list(set(charts[key]['data']['labels'] + i.get("labels", []))))
        charts[key]["data"]['datasets'].append(_visualization_to_dataset(i))
        if metadata:
            charts[key]["metadata"] = {
                **charts[key].get("metadata", {}), **metadata}

    result = list(chart_dict(**chart) for chart in charts.values()) + other
    return (result, [],)


def _create_collection(name, **kwargs):
    return dict(name=name, **kwargs, data=[])


def _get_collection_target(type_):
    if type_ in ("list", "list_item"):
        return "list"
    elif type_ in ("table_item"):
        return "table_row"
    elif type_ in ("table_row"):
        return "table"
    else:
        return None


def _get_collection_name(statistic):
    type_ = statistic.get("type")

    if type_ == "list_item":
        return statistic.get("parameters", {}).get('name')
    elif type_ == "list":
        return statistic.get("payload").get("name")
    elif type_ == "table_item":
        return statistic.get("payload", {}).get('topic_name')
    elif type_ == "table_row":
        return statistic.get("payload").get("table_name")


def _get_collection_kwargs(statistic):
    type_ = statistic.get("type")

    if type_ == "table_item":
        return dict(table_name=statistic.get("parameters", {}).get('name'))
    else:
        return {}


def _get_clean_payload(statistic):
    type_ = statistic.get("type")
    payload = statistic.get("payload", {})

    if type_ == "table_row":
        payload.pop("table_name")
    if type_ in ("list_item", "table_item",):
        topic_name = payload.pop("topic_name")
        payload["payload"]["topic_name"] = topic_name

        try:
            unit = payload.pop("unit")
            payload["payload"]["unit"] = unit
        except KeyError:
            pass

    return payload


def _parse_collections_dict(collections_d):
    result = []

    for type_ in collections_d:
        data = collections_d.get(type_).values()
        result.extend(statistics_dict(type_, **i) for i in data)

    return result


def process_collections(statistics):
    '''Move collection items under the matching collection

    This function must be run twice for tables to be created. First run
    combines table items in a table row and second run combines table rows into
    a table.

    Args:
        statistics: Iterable of statistics

    Returns:
        List of statistics where collection items are moved to a collection.
        Collection statistics are moved to the beginning of the list.
    '''
    collections = dict(list={}, table_row={}, table={})
    other = []
    warnings = []

    for i in statistics:
        if not i:
            continue
        type_ = i.get("type")
        target = _get_collection_target(type_)
        if not target:
            other.append(i)
            continue

        name = _get_collection_name(i)

        payload = _get_clean_payload(i)
        if not name:  # type_ == "list_item"
            warnings.append(
                collection_name_is_undefined(
                    payload.get("method"),
                    payload.get("field")))
            continue

        target_d = collections[target]
        if name not in target_d:
            kwargs = _get_collection_kwargs(i)
            target_d[name] = _create_collection(name, **kwargs)

        if type_ in ("list_item", "table_item", "table_row", ):
            target_d[name]["data"].append(payload)
        elif type_ == "list":
            target_d[name]["data"].extend(payload.get("data", []))

        target_d[name]["metadata"] = {
            **target_d[name].get("metadata", {}),
            **i.get("metadata", {})}

    result = _parse_collections_dict(collections) + other
    return (result, warnings,)


def _process(funcs, statistics):
    data = statistics
    warnings = []

    for f in funcs:
        data, new_warnings = f(data)
        warnings.extend(new_warnings)

    return (data, warnings, )


def pre_process(statistics):
    '''Pre-process the statistics results after the data tools run

    Args:
        statistics: Iterable of statistics

    Returns:
        Pre-processed results and warnings as (results, warnings,) tuple
    '''
    funcs = (
        process_collections,
    )
    return _process(funcs, statistics)


def post_process(statistics):
    '''Post-process the statistics when combining multiple data tool runs

    Args:
        statistics: Iterable of statistics

    Returns:
        Post-processed results and warnings as (results, warnings,) tuple
    '''
    funcs = (
        process_charts,
        process_collections,
    )
    return _process(funcs, statistics)
