from rq.worker import *

import MySQLdb as madb
import config as donk_conf
#Here we try to implement a custom worker class which adds a persistent database connection acros jobs.
#this connection is passed to each job in the kwarg db_conn


class MySQLWorker(Worker):
	def __init__(self, queues, name=None,
				 default_result_ttl=None, connection=None,
				 exc_handler=None, default_worker_ttl=None, job_class=None):  # noqa
		if connection is None:
			connection = get_current_connection()
		self.connection = connection

		queues = [self.queue_class(name=q) if isinstance(q, text_type) else q
				  for q in ensure_list(queues)]
		self._name = name
		self.queues = queues
		self.validate_queues()
		self._exc_handlers = []

		if default_result_ttl is None:
			default_result_ttl = DEFAULT_RESULT_TTL
		self.default_result_ttl = default_result_ttl

		if default_worker_ttl is None:
			default_worker_ttl = DEFAULT_WORKER_TTL
		self.default_worker_ttl = default_worker_ttl

		self._state = 'starting'
		self._is_horse = False
		self._horse_pid = 0
		self._stop_requested = False
		self.log = logger
		self.failed_queue = get_failed_queue(connection=self.connection)
		self.last_cleaned_at = None

		# By default, push the "move-to-failed-queue" exception handler onto
		# the stack
		self.push_exc_handler(self.move_to_failed_queue)
		if exc_handler is not None:
			self.push_exc_handler(exc_handler)

		if job_class is not None:
			if isinstance(job_class, string_types):
				job_class = import_attribute(job_class)
			self.job_class = job_class
		self.mysql_conn= madb.connect(host=donk_conf.MySQL_host,
								user=donk_conf.MySQL_user,
								passwd=donk_conf.MySQL_passwd,
								port=donk_conf.MySQL_port)

		
	def execute_job(self, *args, **kwargs):
		"""Execute job in same thread/process, do not fork()"""
		kwargs['db_conn'] = self.mysql_conn
		return self.perform_job(*args, **kwargs)
