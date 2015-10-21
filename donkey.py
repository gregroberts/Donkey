import config as donk_conf
from redis import Redis
from querier import query as donk_query
import time, grabber, re, json
from datetime import datetime
import MySQLdb as madb
from scheduler import schedule, scheduler
from MySQLdb.cursors import DictCursor


def fill(query, params):
	'''puts params into query'''
	qry = repr(query)
	for i, j in params.items():
		qry = re.sub('{{%s}}' % i, j, qry)
	qry = eval(qry)
	return qry




class Donkey:
	rd_conn = Redis(host = donk_conf.REDIS_HOST,
				port = donk_conf.REDIS_PORT)

	mysql_conn= madb.connect(host=donk_conf.MySQL_host,
					    user=donk_conf.MySQL_user,
					    passwd=donk_conf.MySQL_passwd,
					    port=donk_conf.MySQL_port,
					    db=donk_conf.MySQL_db)
	def query(self, query):
		return donk_query(query)



	def search(self, name = None):
		'''searches the query library for a given term'''
		if name:
			keys = filter(lambda x: name in x.replace('library:',''), self.rd_conn.keys('library:*'))
		else:
			keys = self.rd_conn.keys('library:*')
		results = []
		for i in keys:
			query = self.rd_conn.hmget(i, ['params','description','saved','query'])
			params = eval(query[0])
			description = query[1]
			date_saved = str(datetime.fromtimestamp(float(query[2])))
			qry =  grabber.comp(query[3], un = True)
			res = {
				'name': i.replace('library:',''),
				'description': description,
				'required parameters': params,
				'query':  qry,
				'saved at': date_saved
			}
			results.append(res)
		return results

	def get(self, name):
		'''returns a specified donkey query'''
		try:
			query = self.rd_conn.hmget('library:%s' % name, ['params','description','saved','query'])
			params = eval(query[0] or "[]")
			description = query[1]
			date_saved = str(datetime.fromtimestamp(float(query[2])))
			qry =  grabber.comp(query[3], un = True)
			query = {
				'name': name,
				'description': description,
				'required parameters': params,
				'query':  qry,
				'saved at': date_saved
			}
			return query
		except Exception as e:
			print e
			raise e

	def execute(self, name, params):
		'''runs a specified donkey query'''
		try:
			q = self.get(name)
		except:
			raise 'query name \'%s\' not found' % name
		query = q['query']
		if params.keys() != q['required parameters']:
			raise Exception('Incorrect parameters supplied', 'expecting %s, received %s' % (q['required parameters'], params.keys()))
		else:
			filled_qry = fill(query, params)
			print filled_qry
			result = self.query(filled_qry)
			return result
	def save(self, query, parameters, name, description):
		'''saves the query to th library'''
		to_save = {
			'params':parameters,
			'description':description,
			'saved': time.time(),
			'query':grabber.comp(query)
		}
		self.rd_conn.hmset('library:%s' % name, to_save)
		return 'query saved successfully'

	def collect(self, _input, inputsource, query_archetype, mapping, map_base = '',limit =0, queue_name = 'RT_collection', async = False):
		'''runs a one off collection on RQ'''
		job = {
			'query':query_archetype,
			'putter':{
				'table_name': '@return',
				'base': map_base,
				'mapping':mapping
			}
		}
		job = json.dumps(job)
		t_s = time.time()
		results = schedule(self.rd_conn,_input,job,queue_name, '@OneOff-%d' % t_s, inputsource, limit, self.mysql_conn)
		if async == False:
			res = []
			for i in results: 
				while i.status =='queued' or i.status =='started':
					pass
				print i.status
				if i.status == 'failed':
					res.append(i.exc_info)
				elif i.status == 'finished':
					if type(i.result) == list:
						res.extend(i.result or ['result is None'])
					else:
						res.append(i.result or 'result is None')
				else:
					res.append(i.status)
			return res
		return results

	def setup_collector(self, req):
		c = self.mysql_conn.cursor()
		statement = '''
		INSERT INTO Collections
		(CollectorName, QueueName, Frequency,
		 LastScheduled, InputSource, Input, Archetype, CollectorDescription,InProgress)
		VALUES ('%s','%s',%s,'1970-01-01','%s','%s','%s','%s',0)
		''' % (req['CollectorName'],
			 req['QueueName'],
			 req['Frequency'],
			 req['InputSource'],
			 req['Input'],
			 json.dumps(req['Archetype']).encode('string-escape'),
			 req['CollectorDescription'].replace('\'',''))
		print statement
		c.execute(statement)
		self.mysql_conn.commit()
		return 'ddd'

	def run_collectors(self, names):
		'''if you want to override the normal frequency of a collector,
			provide a list of names to do, and they will be scheduled'''
		scheduler(names, self.mysql_conn)

	def list_collectors(self):
		c = self.mysql_conn.cursor(cursorclass = DictCursor)
		c.execute('SELECT * from Collections')
		collections = c.fetchall()
		return collections

	def check_collector_log(self, name):
		c = self.mysql_conn.cursor(cursorclass = DictCursor)
		c.execute('''SELECT * from Collections_Log
			WHERE CollectorName = \'%s\'
			''' % name)
		return c.fetchall()


if __name__ == '__main__':
	test2 = {
		'request':{
			'url':'http://example.com'
		},
		'handle':{
			'title':'//title//text()'
		}	
	}
	d = Donkey()
	print 'collect'
	for i in d.collect('[{"a":1},{"B":2}]', 'json',test2,{'t':'title[0]'}):
		print i
#	print 'search'
#	print d.search('t')
#	print 'get'
#	print d.get('test')
#
#	print d.query(test2)
#	print 'execute'
#	print d.execute('test', {'url': 'http://example.com'})
#	print 'save'
#	print d.save(test2,[],'testtt','yet another test query')
#	print 'yay, it works'
