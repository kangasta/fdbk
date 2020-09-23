from fdbk.utils.messages import method_not_supported

from ._value_funcs import VALUE_FUNCS as functions
from .utils import status_dict


ASSERTIONS = {
    'eq': lambda a, b: a == b,
    'neq': lambda a, b: a != b,
    'lt': lambda a, b: a < b,
    'lte': lambda a, b: a <= b,
    'gt': lambda a, b: a > b,
    'gte': lambda a, b: a >= b,
    'in': lambda a, b: a in b,
}

OPERATORS = {
    'and': lambda a, b: a and b,
    'or': lambda a, b: a or b,
}


def _get_value(method, data, field, parameters=None):
    value_d = functions.get(method)(data, field, parameters)
    return value_d.get("payload", {}).get("value")


def _get_parameters(parameters=None):
    default = parameters.get("default")
    checks = parameters.get("checks", [])
    short_circuit = parameters.get("short_circuit", False)
    method = parameters.get("method", "latest")

    return default, checks, short_circuit, method


def _run_assertion(assertion, value, other):
    if assertion not in ASSERTIONS:  # pragma: no cover
        raise RuntimeError(f"Assertion {assertion} was not recognized")

    try:
        return ASSERTIONS.get(assertion)(value, other)
    except BaseException:
        return False


def _run_check(value, check):
    status = check.get("status")
    operator = str(check.get("operator", 'or')).lower()

    result = False if operator == 'or' else True

    if operator not in OPERATORS:
        raise RuntimeError(f"Operator {operator} was not recognized")

    for assertion in ASSERTIONS:
        other = check.get(assertion)
        if not other:
            continue

        new_result = _run_assertion(assertion, value, other)
        result = OPERATORS.get(operator)(result, new_result)

    if result:
        return status
    return None


def status(data, field, parameters=None):
    if not len(data):
        return None

    warnings = []
    try:
        default, checks, short_circuit, method = _get_parameters(parameters)
    except BaseException:
        return None

    if method not in functions:
        raise ValueError(method_not_supported(method))

    value = _get_value(method, data, field, parameters)

    status_d = dict(field=field, status=default, reason=None)

    for check in checks:
        try:
            new_status = _run_check(value, check)
        except RuntimeError as error:
            new_status = None
            warnings.append(str(error))

        if new_status:
            status_d["status"] = new_status
            status_d["reason"] = check

            if short_circuit:
                break

    if warnings:
        status_d["metadata"] = {}
        status_d["metadata"]["warnings"] = warnings

    return status_dict(**status_d)


STATUS_FUNCS = dict(
    status=status
)
