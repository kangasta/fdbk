from ._utils import _chart_dict


def doughnut(data, field, type_="doughnut"):
    field_data = [a[field] for a in data]

    if not field_data:
        return None

    return _chart_dict(
        type=type_,
        field=field,
        data=[field_data.count(label) for label in set(field_data)],
        labels=list(set(field_data))
    )


def line(data, field):
    if not data:
        return None

    return _chart_dict(
        type="line",
        field=field,
        data=[{"x": a["timestamp"], "y": a[field]} for a in data],
    )


def pie(data, field):
    return doughnut(data, field, "pie")


CHART_FUNCS = dict(
    doughnut=doughnut,
    line=line,
    pie=pie,
)
