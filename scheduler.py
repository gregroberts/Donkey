#This is the scheduler
#quite simply, you have a sql query which is executed against the database, which returns a set of data.
#then, you have a query archetype, which has placeholders for all the values you want to use


from MySQLdb.cursors import DictCursor
from copy import copy
from rq import Queue
from redis import Redis
from collector import collection, finish
import MySQLdb as madb
import config as donk_conf
import json, time

testing = False
redis_conn = Redis(host = donk_conf.REDIS_HOST,
			 port = donk_conf.REDIS_PORT)



def schedule(redis_conn, _input, archetype, queue_name, collector_name, inputsource = 'sql', limit = 0, mysql_conn = None):
	'''This guy does what it says on the tin. 
	creates a list of jobs for rq, and adds them to the specified queue
	returns set of jobs, if you want to check on them
	'''
	#set async = false for testing
	if mysql_conn is None:
		mysql_conn= madb.connect(host=donk_conf.MySQL_host,
				    user=donk_conf.MySQL_user,
				    passwd=donk_conf.MySQL_passwd,
				    port=donk_conf.MySQL_port,
				    db=donk_conf.MySQL_db)
	q = Queue(queue_name, connection = redis_conn, async= not testing)
	archetype = archetype.replace('"','\\\"')
	db_cursor = mysql_conn.cursor(cursorclass = DictCursor)
	if inputsource == 'sql':
		db_cursor.execute(_input)
		results = db_cursor.fetchall()
	elif inputsource == 'json':
		if isinstance(_input, basestring):
			results = json.loads(_input)
		else:
			results = _input
	job_rets = []
	if limit != 0:
		results = results[:limit]
	db_cursor.execute('''INSERT INTO Collections_Log
			(CollectorName, JobName, TimeStarted,Jobs)
			VALUES ('%s','%s',NOW(),%d)
		''' % (collector_name.split('-')[0], collector_name, len(results)))
	mysql_conn.commit()
	for index, row in enumerate(results):
		job_name = '%s-%d' % (collector_name, index)
		job = copy(archetype)
		for col_n, col_v in row.items():
			job = job.replace('{{%s}}' % col_n, str(col_v))
		job = json.loads(job.decode('string-escape'))
		res = q.enqueue(collection, job,collector_name, job_id= job_name)
		job_rets.append(res)
	#finally, add a job which finishes the collection
	if collector_name[0] != '@':
		#if name starts with @, tis a RT_collection
		q.enqueue(finish, collector_name, len(results))
	return job_rets

def scheduler(which = None, mysql_conn=None):
	'''schedules all the collections which need doing'''
	if mysql_conn is None:
		mysql_conn= madb.connect(host=donk_conf.MySQL_host,
				    user=donk_conf.MySQL_user,
				    passwd=donk_conf.MySQL_passwd,
				    port=donk_conf.MySQL_port,
				    db=donk_conf.MySQL_db)
	cursor = mysql_conn.cursor(cursorclass = DictCursor)
	if which is None:
		cursor.execute('''SELECT * FROM Collections
					 WHERE DATE_ADD(LastScheduled,INTERVAL Frequency DAY) < curdate()
					 and InProgress = 0
					 ''')
	else:
		cursor.execute('''SELECT * from Collections
			where CollectorName in (%s)
			''' % ','.join(map(lambda x: '"%s"' % x, which)))
	jobs = cursor.fetchall()	
	for i in jobs:
		collector_name = '%s-%d' % (i['CollectorName'] , time.time())
		schedule(redis_conn,
			   i['Input'],
			   i['Archetype'],
			   i['QueueName'],
			   collector_name,
			   i['InputSource']
			)
		cursor.execute('''UPDATE Collections 
					SET LastScheduled = curdate() ,
						InProgress = 1
					WHERE CollectorName = \'%s\' ''' % i['CollectorName'])
		mysql_conn.commit()


if __name__ == '__main__':
	scheduler()