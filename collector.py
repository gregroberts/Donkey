#This happy little fella is what will do almost all of the leg work for us
#
#it takes quite a few instructions:
#
#-query instructions
#	this is a dict which is handed up to Donkey (querier.py)  
#	contains request and optionally handler instructions
#
#-putter instructions
#	i.e., how to turn a donkey response into a sql statement
#	-database name
#	-table name
#	-base element: what element of the returned response will contain the things we want to put into a database (should be a JMESPATH query)
#	-mapping: key_value pairs which define the mapping
#	-db_action (e.g. replace,insert) update not supported yet!
#
# also takes: 
#	-db connection
#

from querier import query as d_q
from jmespath import search
from re import findall
from dateutil import parser
from MySQLdb import escape_string
from config import collector_schemaname
from rq import Queue
from redis import Redis
import config as donk_conf

def do_str(_in):
	'''deals with stringlike things'''
	if type(_in) is type(None):
		_in = 'NULL'
		return _in
	if type(_in) is not basestring:
		_in = '%s' % _in
	gg = escape_string(_in.decode('ascii',errors='replace'))
	return ' \' %s \' ' % gg


def finish(job_name,length, db_conn = None):
	'''called once a collection has finished'''
	collector_name = job_name.split('-')[0]
	print 'finishing job %s' % job_name
	redis_conn = Redis(host = donk_conf.REDIS_HOST,
			 port = donk_conf.REDIS_PORT)
#	print collector_name
#	if db_conn == None:
#		#for debug
#		import dbapi
#		db = dbapi.mdb()
#		db_conn = db.keyconn
	db_cursor = db_conn.cursor()
	db_cursor.execute('UPDATE Collections SET InProgress=0 where CollectorName = \'%s\'' % collector_name)
	db_conn.commit()
	failed = Queue('failed', connection = redis_conn, async=False)
	failed_jobs = filter(lambda x: job_name in x.id, failed.jobs)
	failed_reasons = ',\n'.join(i.exc_info for i in failed_jobs)
	failed_reasons = failed_reasons.replace('\'','')
	statement = '''UPDATE Collections_Log
			SET TimeFinished = NOW(),
				Failures = %d,
				ExceptionStrings = '%s'
			WHERE JobName = '%s'
			AND CollectorName = '%s'
	''' % (len(failed_jobs),
		 failed_reasons,
		 job_name,
		 collector_name)
	db_cursor.execute(statement)
	db_conn.commit()


def mk_table(putter_args, db_cursor):
	table_name = putter_args['table_name']
	columns = putter_args['mapping'].keys()
	col_stmnt = ',\n'.join(map(lambda x: '`%s` TEXT(500)' % x,columns))
	statement = '''CREATE TABLE IF NOT EXISTS `%s`.`%s` (
		`id` int(11) NOT NULL AUTO_INCREMENT,
		`CollectorName` varchar(255) DEFAULT '',
		`Collected` datetime DEFAULT 0,
		`etl_status` int(2) DEFAULT 0,
		%s,
		PRIMARY KEY (`id`)
	) ENGINE=InnoDB AUTO_INCREMENT=168 DEFAULT CHARSET=latin1;
	''' % (donk_conf.collector_schemaname, table_name, col_stmnt)
	try:
		db_cursor.execute(statement)
	except Exception as e:
		raise(Exception('%s - %s' % (e,statement)))


def grab(data, params, collector_name):
	'''constructs a single SQL query from a single object
	'''
	k_v = list(params['mapping'].items())
	qry = ' INSERT INTO %s.%s \n' % (donk_conf.collector_schemaname, params['table_name'])
	qry += '(CollectorName, Collected,%s) VALUES \n' % ','.join(map(lambda x: '`%s`' % x[0], k_v))
	vals = [do_str(collector_name.split('-')[0]), 'NOW()']
	for col_name, col_loc in k_v:
		val = search(col_loc, data)
		s_val = do_str(val)
		vals.append(s_val)
	qry += '(%s)' % ','.join(vals)
	return qry



def collect(query_args, putter_args, collector_name, db_conn=None):
	'''does the collection, either puts the data in a table
		or returns it in a dictarray to the caller (in case of real time collection)
	'''
	data = d_q(query_args)
	if putter_args['base'] != '':
		base = search(putter_args['base'], data)
	else:
		base = data
	if putter_args['table_name'] == '@return':
		#return a dictarray to be turned into a table
		if type(base) is list:
			vals = [{key: search(val, i) for key,val in putter_args['mapping'].items()} for i in base]
		elif type(base) is dict:
			vals = {key: search(val, base) for key,val in putter_args['mapping'].items()}
		#print vals
		return vals
	else:
		cursor = db_conn.cursor()
		mk_table(putter_args, cursor)
		db_conn.commit()
		queries = []
		if type(base) is list:
			for i in base:
				qry = grab(i,putter_args, collector_name)
				queries.append(qry)
		elif type(base) is dict:
			queries.append(grab(base, putter_args, collector_name))
		else:
			raise Exception('Data Structure \'%s\' not recognised!' % type(base))
		for qry in queries:
			cursor.execute(qry)
		db_conn.commit()

def collection(args,collector_name, db_conn=None):
	'''runs a collection and returns the result
		(None for a SQL collection, dictarray for one off)'''
#	if db_conn == None:
#		import dbapi
#		db = dbapi.mdb()
#		db_conn = db.keyconn
	query_args = args['query']
	putter_args = args['putter']
	return collect(query_args,putter_args,collector_name, db_conn)



if __name__ == '__main__':
	#test regular collection
	import dbapi
	db = dbapi.mdb()	
	
#	qry = {
#		'query':{
#			'request':{
#				'@grabber':'request',
#				'url':'http://www.amazon.com/product-reviews/1782160000'
#			},
#			'handle':{
#				'reviews':{
#					'@base':'//div[@class=\'a-section review\']',
#					'text':'.//a[contains(@class,\'review-title\')]/text()',
#					'date':'.//span[contains(@class,\'review-date\')]/text()',
#					'empty':'.//span[@class=\'nonexistent\']/text()',
#					'num':'.//span[contains(@class,\'alt\')]/text()'
#				}
#
#			}
#		},
#		'putter':{
#			'table_name':'test',
#			'base':'reviews',
#			'mapping':{
#				'testcol':'num[0]',
#				'testcol1':'empty[0]',
#				'testcol2':'date[0]'
#			}
#		}
#	}
#	collection(qry, db.keyconn)
#	print d_q(qry['query'])#.encode('utf8',errors='replace')
	#test return collection
	qry = {
		'query':{
			'request':{
				'@grabber':'request',
				'url':'http://www.amazon.com/product-reviews/1782160000'
			},
			'handle':{
				'reviews':{
					'@base':'//div[@class=\'a-section review\']',
					'text':'.//a[contains(@class,\'review-title\')]/text()',
					'date':'.//span[contains(@class,\'review-date\')]/text()',
					'empty':'.//span[@class=\'nonexistent\']/text()',
					'num':'.//span[contains(@class,\'alt\')]/text()'
				}

			}
		},
		'putter':{
			'table_name':'@return',
			'base':'reviews',
			'mapping':{
				'testcol':'num[0]',
				'testcol1':'empty[0]',
				'testcol2':'date[0]'
			}
		}
	}
	print collection(qry, db.keyconn)

