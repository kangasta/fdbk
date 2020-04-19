from fdbk.utils.messages import method_not_supported, field_is_undefined

from .functions import functions as data_functions
from .functions.utils import chart_dict


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

        result = data_functions[instruction["method"]](
            data, instruction["field"]
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

    return (results, warnings,)


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

    return list(chart_dict(**chart) for chart in charts.values()) + other


def post_process(statistics):
    return process_charts(statistics)
