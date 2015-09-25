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


def dodate(_in):
	'''parses a datelike thing into a date string'''
	dd = parser.parse(_in)
	ddd = '\' %s\'' % dd
	return ddd

def do_str(_in):
	'''deals with stringlike things'''
	if type(_in) is type(None):
		_in = 'NULL'
		return _in
	if type(_in) is not basestring:
		_in = '%s' % _in
	gg = escape_string(_in.decode('ascii',errors='replace'))
	return ' \' %s \' ' % gg


#maps mysql types to python types
t_maps = {
	'date':dodate,
	'datetime':dodate,
	'timestamp': float,
	'time':dodate,
	'year':int,
	'char':do_str,
	'varchar':do_str,
	'blob':do_str,
	'text':do_str,
	'tinyblob': do_str,
	'tinytext': do_str,
	'mediumblob': do_str,
	'mediumtext':do_str,
	'longblob': do_str,
	'longtext': do_str,
	'enum': repr,
	'intotinyint': int,
	'smallint':int,
	'mediumint':int,
	'bigint': int,
	'float': float,
	'double': float,
	'decimal': float,
}



def finish(job_name, db_conn = None):
	'''called once a collection has finished'''
	db_cursor = db_conn.cursor()
	db_cursor.execute('UPDATE Collections SET InProgress=0 where CollectorName = \'%s\'' % job_name)
	db_conn.commit()


def get_coldefs(cursor, tbl_name):
	'''gets the type of each column'''
	cursor.execute('SHOW COLUMNS from %s.%s' % (collector_schemaname, tbl_name))
	names = map(lambda x: (x[0],x[1]),cursor.fetchall())
	n_d = {}
	for i in names:
		var_name = i[0]
		base_type = findall('(\w+)',i[1])[0].lower()
		n_d[var_name] = t_maps.get(base_type, do_str)
	return n_d


def grab(data, params, cols):
	'''constructs a single SQL query from a single object
	'''
	k_v = list(params['mapping'].items())
	qry = ' %s INTO %s.%s \n' % (params.get('action','REPLACE'), collector_schemaname, params['table_name'])
	qry += '(%s) VALUES \n' % ','.join(map(lambda x: x[0], k_v))
	vals = []
	for col_name, col_loc in k_v:
		val = search(col_loc, data)
		s_val = cols[col_name](val)
		vals.append(s_val)
	qry += '(%s)' % ','.join(vals)
	return qry



def collect(query_args, putter_args,db_conn=None):
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
		return vals
	else:
		cursor = db_conn.cursor()
		cols = get_coldefs(cursor, putter_args['table_name'])
		queries = []
		if type(base) is list:
			for i in base:
				qry = grab(i,putter_args, cols)
				queries.append(qry)
		elif type(base) is dict:
			queries.append(grab(base, putter_args, cols))

		else:
			raise Exception('Data Structure \'%s\' not recognised!' % type(base))
		for qry in queries:
			cursor.execute(qry)
		db_conn.commit()

def collection(args, db_conn):
	'''runs a collection and returns the result
		(None for a SQL collection, dictarray for one off)
	'''
	query_args = args['query']
	putter_args = args['putter']
	return collect(query_args,putter_args, db_conn)



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

