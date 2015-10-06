import sys
sys.path.append('/home/greg/Donkey')
from flask import Flask, request, Response, abort, render_template
from flask.ext.classy import FlaskView, route
import config as donk_conf
from redis import Redis
import grabber
from querier import query as donk_query
from json import dumps
from datetime import datetime
import re, time
from traceback import format_exc
from pprint import pprint
import handlers
from donkey import Donkey
import rq_dashboard
#Donkey Version 3 Web API


#this whole thing could be a lot tidier, but idgaf!



def response(success, body):
	res = {
		'success':success,
		'response':body}
	try:
		return Response(
				response=dumps(res),
				status = 200,
				mimetype='application/json')
	except:
		return Response(
				response=format_exc().split('\n'),
				status=500,
				mimetype='application/json')


class V3View(FlaskView):
	#This is the main view we use for querying and writing queries
	d = Donkey()

	config = {
		'REDIS_HOST':donk_conf.REDIS_HOST,
		'REDIS_PORT':donk_conf.REDIS_PORT
	}

	def index(self):
		return render_template('index.html',
			prefix = donk_conf.web_prefix)

	def docs(self, route ):
		return render_template('%s_docs.html' % route,
			prefix = donk_conf.web_prefix)

	def edit(self, name):
		'''this loads the query editing ui.
		'''
		gg = filter(lambda x: '_grabber' in x, grabber.grabbers.__dict__.keys())
		grabbers = map(lambda x: x.replace('_grabber',''),gg)
		handles = filter(lambda x: x.upper() == x, handlers.__dict__.keys())
		if name != 'new':
			query = self.d.get(name)
		else:
			query = {}
		return render_template('query_editor.html',
						 grabbers = grabbers,
						 handlers = handles,
						 query = query,
						 prefix = donk_conf.web_prefix
						)

	def search(self, query = None):
		queries = self.d.search(query)
		for i in queries:
			i['query'] = dumps(i['query'], indent=4)
		return render_template('list_queries.html',
						results = queries,
						n = len(queries),
						prefix = donk_conf.web_prefix)
	def list(self):
		return self.search()

	def collect(self, name):
		gg = filter(lambda x: '_grabber' in x, grabber.grabbers.__dict__.keys())
		grabbers = map(lambda x: x.replace('_grabber',''),gg)
		handles = filter(lambda x: x.upper() == x, handlers.__dict__.keys())
		if name != 'new':
			query = self.d.get(name)
		else:
			query = {}		
		return render_template('collect_single.html',
						 grabbers = grabbers,
						 handlers = handles,
						 query = query,
						 prefix = donk_conf.web_prefix
						)

	@route('/run_collectors/',methods = ['POST'])
	def run_collectors(self):
		names =request.json
		print names
		self.d.run_collectors(names)
		return response(True,{'message':'Collectors have been added'})

	@route('/setup_collector/', methods = ['POST'])
	def setup_collector(self):
		req = request.json
		try:
			res =self.d.setup_collector(req)
		except:
			print 'dddddd'
			res = format_exc()
			print res
		return res

	def collectors(self):
		collectors = self.d.list_collectors()
		return render_template('collectors.html',
						prefix = donk_conf.web_prefix,
						n = len(collectors),
						collectors = collectors)

	def collector_log(self, name):
		rows = self.d.check_collector_log(name)
		return render_template('collector_log.html',
						prefix = donk_conf.web_prefix,
						rows = rows,
						name = name
						)


	@route('/collection/', methods = ['POST'])
	def collection(self):
		args = request.json
		try:
			result = list(self.d.collect(args['input'],
							args['inputsource'],
							args['archetype'],
							args['mapping'],
							args['map_base'],
							#if limit not set, assume 0
							args.get('limit', 0),
							#collections through the web api always put on same queue
							))
			success = True
		except:
			success = False
			result = format_exc().split('\n')
		return response(success, result)


	def get_query(self, name):
		'''searches for the query matching name,
		returns the hydrated query 
		or an error message
		(accepts GET)
		'''
		if request.method != 'GET':
			abort(405)
		try:
			res = self.d.get(name)
			success = True

		except Exception as e:
			res = {
				'message':'error accessing Redis Query Library',
				'exception':e
			}
			success = False
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
		try:
			qry = self.d.execute(name, request.args)
			res = {
				'query name':name,
				'result':qry
			}
			success = True
		except Exception as e:
			res = {
				'name':name,
				'exception message': str(e),
				'exception traceback':format_exc().split('\n')
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
		(accepts POST)'''
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
		try:
			msg = self.d.save(query['query'], query['parameters'], query['description'])
			success = True
		except:
			msg = format_exc().split('\n')
			success = False

		res = {'message':msg}
		return response(success, res)

	def search_queries(self,val):
		'''searches for all queries matching val
		returns the json in  a nice list
		ordered alphabetically
		(accepts GET)'''
		if request.method != 'GET':
			abort(405)
		results = self.d.search(val)
		res = {
			'query':val,
			'n_results':len(results),
			'results':results
		}
		success = True
		return response(success, res)

	def list_queries(self):
		'''Lists all the queries in the library
		(accepts GET)'''
		if request.method != 'GET':
			abort(405)
		results = self.d.search()
		res = {
			'queries':results,
			'number of queries':len(results)
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
				'response':self.d.query(query)
			}
			success= True
		except Exception as e:
			print e
			res = {
				'query':query,
				'exception message': e.args[0],
				'exception traceback':format_exc().split('\n')
			}
			success = False
		return response(success, res)		



application = Flask(__name__)
application.config['REDIS_HOST'] = donk_conf.REDIS_HOST
application.config['REDIS_PORT'] = donk_conf.REDIS_PORT
application.config['RQ_POLL_INTERVAL'] = 3000
application.config['APPLICATION_ROOT'] = donk_conf.web_prefix
application.register_blueprint(rq_dashboard.blueprint, url_prefix='/v3/dashboard' )
V3View.register(application)



if __name__==  '__main__':
	application.run(host='0.0.0.0',debug = True)