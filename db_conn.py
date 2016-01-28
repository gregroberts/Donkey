import config as conf
import MySQLdb, sqlite3

class DB:
	conn = None

	def __init__(self, backend = conf.SQL_BACKEND, db_name = conf.sql_schemaname):
		self.backend = backend
		self.db_name = db_name
		self.connect()

	def connect(self):
		if self.backend == 'mysql':
			self.conn = MySQLdb.connect(**conf.SQL_CONF)
			self.errs = (AttributeError, MySQLdb.OperationalError)
		elif self.backend == 'sqlite':
			self.conn = sqlite3.connect(self.db_name)
			self.errs = ()
		else:
			raise Exception('Unknown backend %s' % backend)

	def query(self, sql, **cursor_kwargs):
		res = []
		if self.backend == 'mysql':
			try:
				c = self.conn.cursor(**cursor_kwargs)
	 			c.execute(sql)
	 			res = c.fetchall()
			except self.errs:
				self.connect()
				c = self.conn.cursor(**cursor_kwargs)
	 			c.execute(sql)
	 			res = c.fetchall()
		elif self.backend == 'sqlite':
			#because I don't understand how/if sqlite's context manager works =/
			c = self.conn.cursor(**cursor_kwargs)
			c.execute(sql)
			res = c.fetchall()
		self.conn.commit()
		return res

