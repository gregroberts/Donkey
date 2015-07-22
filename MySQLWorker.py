from rq.worker import *
import time, sys
import MySQLdb as madb
import config as donk_conf
#Here we try to implement a custom worker class which adds a persistent database connection acros jobs.
#this connection is passed to each job in the kwarg db_conn


class MySQLWorker(Worker):
	def __init__(self, queues, interval= 5, name=None,
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
								port=donk_conf.MySQL_port,
								db=donk_conf.MySQL_db)
		#makes sure we only do a job once interval has expired
		self.last_job = time.time()
		self.interval = interval

	def perform_job(self, job):
		"""Performs the actual work of a job.  Will/should only be called
		inside the work horse's process.
		"""
		#make sure we dont do more than one job per interval
		sms = ['\\','|','/','-']
		while int(time.time()) < int(self.interval + self.last_job):
			for i in sms:
				sys.stdout.write('%s\r' % i)
		self.prepare_job_execution(job)
		job.kwargs['db_conn'] = self.mysql_conn
		with self.connection._pipeline() as pipeline:
			started_job_registry = StartedJobRegistry(job.origin, self.connection)
			try:
				with self.death_penalty_class(job.timeout or self.queue_class.DEFAULT_TIMEOUT):
					rv = job.perform()

				# Pickle the result in the same try-except block since we need
				# to use the same exc handling when pickling fails
				job._result = rv

				self.set_current_job_id(None, pipeline=pipeline)

				result_ttl = job.get_result_ttl(self.default_result_ttl)
				if result_ttl != 0:
					job.ended_at = utcnow()
					job._status = JobStatus.FINISHED
					job.save(pipeline=pipeline)

					finished_job_registry = FinishedJobRegistry(job.origin, self.connection)
					finished_job_registry.add(job, result_ttl, pipeline)

				job.cleanup(result_ttl, pipeline=pipeline)
				started_job_registry.remove(job, pipeline=pipeline)

				pipeline.execute()

			except Exception:
				job.set_status(JobStatus.FAILED, pipeline=pipeline)
				started_job_registry.remove(job, pipeline=pipeline)
				pipeline.execute()
				self.handle_exception(job, *sys.exc_info())
				#TODO Add a bit here which informs the server of the failed collection
				return False

		if rv is None:
			self.log.info('Job OK')
		else:
			self.log.info('Job OK, result = {0!r}'.format(yellow(text_type(rv))))

		if result_ttl == 0:
			self.log.info('Result discarded immediately')
		elif result_ttl > 0:
			self.log.info('Result is kept for {0} seconds'.format(result_ttl))
		else:
			self.log.warning('Result will never expire, clean up result key manually')
		self.last_job = time.time()
		print self.last_job
		return True

