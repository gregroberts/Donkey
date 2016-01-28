#This is the scheduler
#quite simply, you have a sql query which is executed against the database, which returns a set of data.
#then, you have a query archetype, which has placeholders for all the values you want to use


from MySQLdb.cursors import DictCursor
from copy import copy
from rq import Queue
from redis import Redis
from collector import collection, finish
from db_conn import DB
import config as donk_conf
import json, time

testing = False
redis_conn = Redis(**donk_conf.REDIS_CONF)



def schedule(redis_conn, _input, archetype, queue_name, collector_name, inputsource = 'sql', limit = 0, db_conn = None):
	'''This guy does what it says on the tin. 
	creates a list of jobs for rq, and adds them to the specified queue
	returns set of jobs, if you want to check on them
	'''
	#set async = false for testing
	if db_conn is None:
		db_conn= DB()
	q = Queue(queue_name, connection = redis_conn, async= not testing)
	archetype = archetype.replace('"','\\\"')
	if inputsource == 'sql':
		results = db_conn.query(_input, cursorclass = DictCursor)
	elif inputsource == 'json':
		if isinstance(_input, basestring):
			results = json.loads(_input)
		else:
			results = _input
	job_rets = []
	if limit != 0:
		results = results[:limit]
	db_conn.query('''INSERT INTO Collections_Log
			(CollectorName, JobName, TimeStarted,Jobs)
			VALUES ('%s','%s',NOW(),%d)
		''' % (collector_name.split('-')[0], collector_name, len(results)))
	for index, row in enumerate(results):
		job_name = '%s-%d' % (collector_name, index)
		job = copy(archetype)
		for col_n, col_v in row.items():
			job = job.replace('{{%s}}' % col_n, str(col_v))
		job = json.loads(job.decode('string-escape'))
		res = q.enqueue(collection, job,collector_name, job_id= job_name)
		job_rets.append(res)
	print finish, collector_name, len(results)
	#finally, add a job which finishes the collection
	q.enqueue(finish, collector_name, len(results))
	return job_rets

def scheduler(which = None, db_conn=None):
	'''schedules all the collections which need doing'''
	if db_conn is None:
		db_conn= DB()
	db_conn.query('''
		CREATE TABLE IF NOT EXISTS Collections (
			id INT(3) AUTO_INCREMENT ,
			CollectorName VARCHAR(45),
			QueueName VARCHAR(40),
			Frequency INT(5),
	 		LastScheduled DATETIME DEFAULT '1970-01-01',
	 		InputSource VARCHAR(10),
	 		Input VARCHAR(900), 
	 		Archetype VARCHAR(999),
	 		CollectorDescription VARCHAR(999),
	 		InProgress INT(2) DEFAULT 0,
	 		PRIMARY KEY (id)
	 	)
		''')
	db_conn.query('''
		CREATE TABLE IF NOT EXISTS Collections_Log (
			id INT(10) AUTO_INCREMENT,
			CollectorName VARCHAR(50),
			JobName VARCHAR(50),
			TimeStarted DATETIME,
			Jobs INT(10),
			Failures INT(10),
			ExceptionStrings VARCHAR(50),
			PRIMARY KEY (id)
		)''')
	if which is None:
		jobs = db_conn.query('''SELECT * FROM Collections
					 WHERE DATE_ADD(LastScheduled,INTERVAL Frequency DAY) <= curdate()
					 and InProgress = 0
					 ''',
					 cursorclass = DictCursor)
	else:
		jobs = db_conn.query('''SELECT * from Collections
			where CollectorName in (%s)
			''' % ','.join(map(lambda x: '"%s"' % x, which)),
			cursorclass = DictCursor)	
	for i in jobs:
		collector_name = '%s-%d' % (i['CollectorName'] , time.time())
		schedule(redis_conn,
			   i['Input'],
			   i['Archetype'],
			   i['QueueName'],
			   collector_name,
			   i['InputSource']
			)
		db_conn.query('''UPDATE Collections 
					SET LastScheduled = curdate() ,
						InProgress = 1
					WHERE CollectorName = \'%s\' ''' % i['CollectorName'])


if __name__ == '__main__':
	scheduler()
