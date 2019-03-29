from importlib import import_module

def create_db_connection(db_connection, db_parameters):
	try:
		db_connection_mod = import_module("fdbk." + db_connection)
		return db_connection_mod.ConnectionClass(*db_parameters)
	except Exception as e:
		raise RuntimeError("Loading or creating fdbk DB connection failed: " + str(e))
