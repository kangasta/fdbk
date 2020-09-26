from fdbk.utils.messages import (
    method_not_supported,
    field_is_undefined,
    no_data)

from .functions import functions as data_functions, CHART_FUNCS
from ._aggregate import aggregate
from ._process import pre_process, post_process


def _get_warnings_from_metadata(statistic):
    if not statistic:
        return []

    metadata = statistic.get("metadata")
    if not metadata:
        return []

    warnings = metadata.get("warnings")
    if not warnings:
        return []

    return list(warnings)


def _check_data_tool(data_tool, topic_d):
    if data_tool["method"] not in data_functions:
        raise ValueError(method_not_supported(data_tool["method"]))
    if data_tool["field"] not in topic_d["fields"]:
        raise ValueError(field_is_undefined(data_tool["field"]))


def _add_topic_and_metadata(statistic, topic_d, instruction):
    if not statistic:
        return

    statistic["payload"]["topic_name"] = topic_d["name"]
    if instruction.get("metadata"):
        statistic["metadata"] = instruction.get("metadata")
    try:
        statistic["payload"]["unit"] = next(
            i["unit"] for i in topic_d["units"] if (
                i["field"] == instruction["field"])
        )
    except StopIteration:
        pass


def run_data_tools(
        topic_d,
        data,
        aggregate_to=None,
        aggregate_with=None,
        aggregate_always=False):
    '''Run data tools of topic for given data

    Args:
        topic_d: Topic of which data tools to run
        data: Data to run the data tools against
        aggregate_to: Aggregate data into specified number of data points
        aggregate_with: Aggregate data with speficied function
        aggregate_always: Aggregate data even if datas length is
            shorter than aggregate_to value. Disabled by default.

    Returns:
        Pre-processed results and warnings as (results, warnings,) tuple
    '''
    results = []
    warnings = []

    if not data:
        warnings.append(no_data(topic_d))
        return ([], warnings,)

    if aggregate_to:
        chart_data, aggregate_warnings = aggregate(
            data, aggregate_to, aggregate_with, aggregate_always)
        warnings.extend(aggregate_warnings)
    else:
        chart_data = data

    for instruction in topic_d['data_tools']:
        try:
            _check_data_tool(instruction, topic_d)
        except ValueError as error:
            warnings.append(str(error))
            continue

        is_chart = instruction["method"] in CHART_FUNCS

        try:
            result = data_functions[instruction.get("method")](
                data if not is_chart else chart_data,
                instruction.get("field"),
                instruction.get("parameters")
            )
        except ValueError as error:
            warnings.append(str(error))
            result = None

        warnings.extend(_get_warnings_from_metadata(result))
        _add_topic_and_metadata(result, topic_d, instruction)
        results.append(result)

    results, pre_warnings = pre_process(results)
    warnings.extend(pre_warnings)
    return (results, warnings,)


def combine_run_outputs(outputs):
    '''Combine results and warnings from multiple runs

    Args:
        outputs: Iterable of (results, warnings,) tuples

    Returns:
        Post-processed results and warnings as (results, warnings,) tuple
    '''
    results = []
    warnings = []

    for new_results, new_warnings in outputs:
        results.extend(new_results)
        warnings.extend(new_warnings)

    results, post_warnings = post_process(results)
    warnings.extend(post_warnings)

    return (results, warnings,)
