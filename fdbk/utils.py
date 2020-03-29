from argparse import ArgumentParser
from importlib import import_module

BUILT_IN = dict(
    client="fdbk._client_connection",
    ClientConnection="fdbk._client_connection",
    dict="fdbk._dict_connection",
    DictConnection="fdbk._dict_connection",
)


def create_db_connection(db_plugin, db_parameters):
    if db_plugin in BUILT_IN.keys():
        db_plugin = BUILT_IN.get(db_plugin)

    try:
        db_connection_mod = import_module(db_plugin)
        return db_connection_mod.ConnectionClass(*db_parameters)
    except Exception as e:
        raise RuntimeError(
            "Loading or creating fdbk DB connection failed: " + str(e))


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


def visualizations_to_charts(visualizations):
    charts = {}

    for i in visualizations:
        if not i:
            continue

        field = i.get('field')
        type_ = i.get('type')
        key = f"{field}-{type_}"

        if key not in charts:
            charts[key] = _create_chart(type_, field)

        charts[key]['data']['labels'] = (
            list(set(charts[key]['data']['labels'] + i.get("labels", []))))
        charts[key]["data"]['datasets'].append(_visualization_to_dataset(i))

    return list(charts.values())


def get_reporter_argparser(parser=None):
    if not parser:
        parser = ArgumentParser()

    parser.add_argument(
        "db_parameters",
        nargs="+",
        type=str,
        help="Parameters for fdbk DB connection.")
    parser.add_argument(
        "--db-connection",
        type=str,
        default="ClientConnection",
        help="fdbk DB connection to use (default=ClientConnection)")
    parser.add_argument(
        "--interval",
        "-i",
        type=float,
        default=360.0,
        help="Data pushing interval in seconds.")
    parser.add_argument(
        "--num-samples",
        "-n",
        type=int,
        default=60,
        help="Number of samples to average during the push interval")
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print progress messages")

    return parser
