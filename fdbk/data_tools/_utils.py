from fdbk.utils.messages import (
    method_not_supported, field_is_undefined, list_name_is_undefined)

from .functions import functions as data_functions
from .functions.utils import chart_dict, statistics_dict


def _create_chart(type_, field):
    return dict(
        field=field,
        type=type_,
        data=dict(datasets=[], labels=[]),
    )


def _create_collection(name):
    return dict(name=name, data=[])


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


def process_lists(statistics):
    lists = {}
    other = []
    warnings = []

    for i in statistics:
        if not i:
            continue
        type_ = i.get("type")
        if type_ not in ("list", "list_item"):
            other.append(i)
            continue

        if type_ == "list_item":
            list_name = i.get("parameters", {}).get('name')
        else:
            list_name = i.get("payload").get("name")

        payload = i.get("payload", {})
        if not list_name:  # type_ == "list_item"
            warnings.append(
                list_name_is_undefined(
                    payload.get("method"),
                    payload.get("field")))
            continue

        if list_name not in lists:
            lists[list_name] = _create_collection(list_name)

        if type_ == "list_item":
            lists[list_name]["data"].append(payload)
        else:
            lists[list_name]["data"].extend(payload.get("data", []))

        lists[list_name]["metadata"] = {
            **lists[list_name].get("metadata", {}),
            **i.get("metadata")}

    result = list(statistics_dict("list", **i) for i in lists.values()) + other
    return (result, warnings,)


def _process(funcs, statistics):
    data = statistics
    warnings = []

    for f in funcs:
        data, new_warnings = f(data)
        warnings.extend(new_warnings)

    return (data, warnings, )


def pre_process(statistics):
    funcs = (
        process_lists,
    )
    return _process(funcs, statistics)


def post_process(statistics):
    funcs = (
        process_charts,
        process_lists,
    )
    return _process(funcs, statistics)


def run_data_tools(topic_d, data):
    results = []
    warnings = []

    for instruction in topic_d['data_tools']:
        if instruction["method"] not in data_functions:
            warnings.append(method_not_supported(instruction["method"]))
            continue
        if instruction["field"] not in topic_d["fields"]:
            warnings.append(field_is_undefined(instruction["field"]))
            continue

        result = data_functions[instruction.get("method")](
            data, instruction.get("field"), instruction.get("parameters")
        )
        if result is not None:
            result["payload"]["topic_name"] = topic_d["name"]
            if instruction.get("metadata"):
                result["metadata"] = instruction.get("metadata")
            try:
                result["payload"]["unit"] = next(
                    i["unit"] for i in topic_d["units"] if (
                        i["field"] == instruction["field"])
                )
            except StopIteration:
                pass

        results.append(result)

    results, pre_warnings = pre_process(results)
    warnings.extend(pre_warnings)
    return (results, warnings,)
