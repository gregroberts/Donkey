from .. import db_conn

def test_get_dbconn_sqlite():
	g = db_conn.DB('sqlite','testdb.db')

def test_get_dbconn_mysql():
	g = db_conn.DB('mysql','test')

