from flask import Flask, request, Response, abort
from flask.ext.classy import FlaskView, route
import config as donk_conf
from redis import Redis
from grabber import comp 
from querier import query as donk_query
from json import dumps
from datetime import datetime
import re, time
from traceback import format_exc
#Donkey Version 3 Web API


#this whole thing could be a lot tidier, but idgaf!


def fill(query, params):
	'''puts params into query'''
	qry = repr(query)
	for i, j in params.items():
		qry = re.sub('{{%s}}' % i, j, qry)
	qry = eval(qry)
	return qry

def response(success, body):
	res = {
		'success':success,
		'response':body,
	}
	return Response(
			response=dumps(res),
			status = 200,
			mimetype='application/json')


class V3View(FlaskView):
	#This is the main view we use for querying and writing queries

	rd_conn = Redis(host = donk_conf.REDIS_HOST,
				port = donk_conf.REDIS_PORT)

	def index(self):
		return 'yo, it works!<br> I should probably replace this with a help section'

	def get_query(self, name):
		'''searches for the query matching name,
		returns the hydrated query 
		or an error message
		(accepts GET)
		'''
		if request.method != 'GET':
			abort(405)
		query = self.rd_conn.hmget('library:%s' % name, ['params','description','saved','query'])
		if query[0] is None:
			res = {'message': 'Query name \'%s\' not found' % name}
			success = False
		else:
			params = eval(query[0])
			description = query[1]
			date_saved = str(datetime.fromtimestamp(float(query[2])))
			qry =  comp(query[3], un = True)
			res = {
				'name': name,
				'description': description,
				'required parameters': params,
				'query':  qry,
				'saved at': date_saved
			}
			success = True
		return response(success, res)

	def execute_query(self, name):
		'''gets the query,fills it with parameters
		then executes
		if query not found, returns same as query
		if full params not supplied, returns that error
		if error further down the stack, returns that.
		(accepts GET)
		'''
		if request.method != 'GET':
			abort(405)
		query = self.rd_conn.hmget('library:%s' % name, ['params','description','saved','query'])
		if query[0] is None:
			res = {'message': 'Query name \'%s\' not found' % name}
			success = False
		else:
			params = eval(query[0])
			description = query[1]
			date_saved = str(datetime.fromtimestamp(float(query[2])))
			qry =  comp(query[3], un = True)
			if request.args.keys() != params:
				res = {
					'message':'supplied params do not match query parameters',
					'supplied parameters':request.args.keys(),
					'required parameters':params
				}
				success = False
			else:
				filled_qry = fill(qry, request.args)
				try:
					result = donk_query(filled_qry)
					res = {
						'query':filled_qry,
						'name':name,
						'result':result
					}
					success = True
				except Exception as e:
					res = {
						'query':filled_qry,
						'name':name,
						'exception message': e.args[0][0],
						'exception traceback':e.args[0][1].split('\n')
					}
					success = False
		return response(success, res)

	@route('/save_query/', methods = ['POST'])
	def save_query(self):
		'''data must include:
			-query as json
			-list of args
			-name of query
			-description of what query does
		(accepts POST)
		'''
		query = request.json
		req_types = {
			'query':dict,
			'parameters':list,
			'name':basestring,
			'description':basestring
		}
		for name, _type in req_types.items():
			if name not in query.keys():
				res = {'message':'%s not stated' % name}
				return response(False,res)
			if not isinstance(query[name], _type):
				args = (name, _type, type(query[name]))
				res = {'message':'argument %s should be %s, instead, got %s' % args}
		to_save = {
			'params':query['parameters'],
			'description':query['description'],
			'saved':time.time(),
			'query':comp(query['query'])
		}
		try:
			self.rd_conn.hmset('library:%s' % query['name'], to_save)
			res = {'message':'query saved successfully'}
			success = True
		except:
			exc = format_exc()
			res = {'message':'query save failed',
				  'exception':exc.split('\n')}
			success = False
		return response(success, res)

	def search(self,val):
		'''searches for all queries matching val
		returns the json in  a nice list
		ordered alphabetically
		(accepts GET)'''
		if request.method != 'GET':
			abort(405)
		keys = filter(lambda x: val in x, self.rd_conn.keys('library:*'))
		results = []
		for i in keys:
			query = self.rd_conn.hmget(i, ['params','description','saved','query'])
			params = eval(query[0])
			description = query[1]
			date_saved = str(datetime.fromtimestamp(float(query[2])))
			qry =  comp(query[3], un = True)
			res = {
				'name': i.replace('library:',''),
				'description': description,
				'required parameters': params,
				'query':  qry,
				'saved at': date_saved
			}
			results.append(res)
		res = {
			'query':val,
			'n_results':len(results),
			'results':results
		}
		success = True
		return response(success, res)

	@route('/test_query/', methods=['POST'])
	def test_query(self):
		'''data must be an executable query
		returns the result of executing that query
		(accepts POST)'''
		query = request.json
		try:
			res = {
				'query':query,
				'response':donk_query(query)
			}
			success= True
		except Exception as e:
			print e
			res = {
				'query':query,
				'exception message': e.args[0][0],
				'exception traceback':e.args[0][1].split('\n')
			}
			success = False
		return response(success, res)		


application = Flask(__name__)
V3View.register(application)


if __name__==  '__main__':
	application.run(host='0.0.0.0',debug = True)