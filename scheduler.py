#This is the scheduler
#quite simply, you have a sql query which is executed against the database, which returns a set of data.
#then, you have a query archetype, which has placeholders for all the values you want to use


from MySQLdb.cursors import DictCursor
from copy import copy
from rq import Queue
from redis import Redis
from collector import collection
from config import *

def schedule(db_conn,redis_conn, sql_query, archetype, queue_name):
	'''This guy does what it says on the tin. 
	creates a list of jobs for rq, and adds them to the specified queue
	'''
	q = Queue(queue_name, connection = redis_conn)
	c = db_conn.cursor(cursorclass = DictCursor)
	c.execute(sql_query)
	results = c.fetchall()
	for row in results:
		job = copy(archetype)
		for col_n, col_v in row.items():
			job = job.replace('{{%s}}' % col_n, col_v)
		job = eval(job)
		q.enqueue(collection, job)



if __name__ == '__main__':
	import dbapi
	db = dbapi.mdb()
	conn = db.keyconn
	redis_conn = Redis(host = REDIS_HOST,
				port = REDIS_PORT)
	sql_query = '''SELECT isbn_10_digit from oss_books where published_date is not null
				and isbn_10_digit is not null
			 limit 10'''
	qry = {
		'query':{
			'request':{
				'grabber':'request',
				'kwargs':{'url':'http://www.amazon.com/dp/{{isbn_10_digit}}'}
			},
			'handle':{
				"title":"//title//text()",
				"author":"//a[contains(@class,'NameID')]//text()"	
			}
		},
		'putter':{
			'table_name':'test',
			'base':'',
			'mapping':{
				'testcol1':'title[0]',
				'testcol2':'author[0]'
			}
		}
	}
	
	queue_name = 'default'
	schedule(conn,
		redis_conn,
		sql_query,
		repr(qry),
		queue_name)