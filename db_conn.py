

import config as conf


def get_dbconn(db_name = conf.sql_schemaname, backend = conf.SQL_BACKEND):
	if backend == 'sqlite':
		import sqlite3
		db = sqlite3.connect(db_name)
	elif backend == 'mysql':
		import MySQLdb
		db = MySQLdb.connect(db = db_name,**conf.SQL_CONF)
		c = db.cursor()
		c.execute('CREATE DATABASE IF NOT EXISTS `%s`;' %db_name)
		db.commit()		
	else:
		raise Exception('Invalid SQL_BACKEND %s' % backend )
	return db
