from .. import db_conn

def test_get_dbconn_sqlite():
	db_conn.get_dbconn('testdb.db', 'sqlite')

def test_get_dbconn_mysql():
	db_conn.get_dbconn('test','mysql')

	