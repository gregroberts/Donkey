#This is the scheduler
#quite simply, you have a sql query which is executed against the database, which returns a set of data.
#then, you have a query archetype, which has placeholders for all the values you want to use


from MySQLdb.cursors import DictCursor
from copy import copy
from rq import Queue
from redis import Redis
from collector import collection
import MySQLdb as madb
import config as donk_conf
import json


def schedule(db_cursor,redis_conn, _input, archetype, queue_name, job_name, inputsource = 'sql'):
	'''This guy does what it says on the tin. 
	creates a list of jobs for rq, and adds them to the specified queue
	'''
	q = Queue(queue_name, connection = redis_conn)
	if inputsource == 'sql':
		db_cursor.execute(_input)
		results = db_cursor.fetchall()
	for index, row in enumerate(results):
		job_name = '%s-%d' % (job_name, index)
		job = copy(archetype)
		for col_n, col_v in row.items():
			job = job.replace('{{%s}}' % col_n, col_v)
		print job
		job = json.loads(job.decode('string-escape'))
		q.enqueue(collection, job, job_id= job_name)



def scheduler():
	mysql_conn= madb.connect(host=donk_conf.MySQL_host,
					    user=donk_conf.MySQL_user,
					    passwd=donk_conf.MySQL_passwd,
					    port=donk_conf.MySQL_port,
					    db=donk_conf.MySQL_db)
	redis_conn = Redis(host = donk_conf.REDIS_HOST,
				 port = donk_conf.REDIS_PORT)
	cursor = mysql_conn.cursor(cursorclass = DictCursor)
	cursor.execute('''SELECT * FROM Collections
				 WHERE DATE_ADD(LastScheduled,INTERVAL Frequency DAY) < curdate()''')
	jobs = cursor.fetchall()
	for i in jobs:
		schedule(cursor,
			   redis_conn,
			   i['Input'],
			   i['Archetype'],
			   i['QueueName'],
			   i['CollectorName'],
			   i['InputSource']
			)
		cursor.execute('''UPDATE Collections 
					SET LastScheduled = curdate() 
					WHERE CollectorName = \'%s\' ''' % i['CollectorName'])
	mysql_conn.commit()


if __name__ == '__main__':
	scheduler()