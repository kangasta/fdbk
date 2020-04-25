'''Utilities for creating DB connection from commandline arguments
'''

from argparse import ArgumentParser
from importlib import import_module

BUILT_IN = dict(
    client="fdbk._client_connection",
    ClientConnection="fdbk._client_connection",
    dict="fdbk._dict_connection",
    DictConnection="fdbk._dict_connection",
)


def process_db_parameters(db_parameters):
    '''Process commandline arguments to DB parameters

    Make parameters with "=" in them into keyword arguments.

    Args:
        db_parameters: Array of commandline arguments given to DB connection

    Returns:
        (args, kwargs) tuple to expand in DB connection creation
    '''
    args = []
    kwargs = {}

    for i in db_parameters:
        if "=" in i:
            key, value = i.split("=", 1)
            kwargs[key] = value
        else:
            args.append(i)

    return (args, kwargs, )


def create_db_connection(db_plugin, db_parameters):
    '''Create DB connection from plugin name and commandline arguments

    Args:
        db_plugin: Name of the DB plugin to use.
        db_parameters: commandline arguments for DB plugin.

    Returns:
        Created DB connection

    Raises:
        RuntimeError: Creating DB connection failed.
    '''
    if db_plugin in BUILT_IN.keys():
        db_plugin = BUILT_IN.get(db_plugin)

    args, kwargs = process_db_parameters(db_parameters)

    try:
        db_connection_mod = import_module(db_plugin)
        return db_connection_mod.ConnectionClass(*args, **kwargs)
    except Exception as e:
        raise RuntimeError(
            "Loading or creating fdbk DB connection failed: " + str(e))


def get_connection_argparser(parser=None):
    '''Create argparser for creating DB connections

    Args:
        parser: argparser to add arguments to. New parser is created by default
            or when parser is falsy.

    Returns:
        Crated or modified parser
    '''
    if not parser:
        parser = ArgumentParser()

    parser.add_argument(
        "db_parameters",
        nargs="*",
        type=str,
        help="Parameters for fdbk DB connection.")
    parser.add_argument(
        "--db-connection",
        type=str,
        default="ClientConnection",
        help="fdbk DB connection to use (default=ClientConnection)")

    return parser
