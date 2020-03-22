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
