import grabber
from handler import handle
from jmespath import search
from copy import copy
import config
from pprint import pprint
import json, re
from datetime import datetime



class Query:
	#this is the basic unit of work in Donkey
	def __init__(self, grabber = None, freshness = None, handler= None):
		self.grabber = grabber or config.default_grabber
		if freshness == None:
			self.freshness = config.default_freshness
		else:
			self.freshness = freshness
		self.handler = handler or config.default_handler
		self.raw_data = ''
		self.data = []
		self.handle_query = {}
		self.request_query = {}
		self.crawl_query = {}

	def fetch(self,update = True, **qry):
		kwargs = copy(qry)
		if self.request_query == None or update:
			self.request_query = qry
		self.raw_data = grabber.request(self.grabber,
								self.freshness,
								kwargs)
		return self

	def handle(self, update=True, **qry):
		if self.handle_query == None or update:
			self.handle_query = qry
		self.data = handle(self.handler, self.raw_data, qry)
		return self

	def crawl(self,next, max_depth = 10):
		all_data = []
		qry = copy(self.request_query)
		if type(self.data) is list:
			all_data.extend(self.data)
		else:
			all_data.append(self.data)
		iters = 1
		check_rule = lambda : len(self.data)>0
		while iters < max_depth and check_rule():
			qry.update(self.handle(update=False,**next).data)
			self.fetch(update = False,**qry).handle(**self.handle_query)
			_new = self.data
			if type(_new) is list:
				all_data.extend(_new)
			else:
				all_data.append(_new)
			iters += 1
		self.crawl_query = {'max_depth':max_depth, 'next':next}
		return all_data

	def run(self, **kwargs):
		query = json.dumps(self.request_query)
		for key, val in kwargs.items():
			query = query.replace('{{%s}}' % key, val)
		query = json.loads(query)
		data = self.fetch(False, **query).handle(False, **self.handle_query).data
		if self.crawl_query != {}:
			data = self.crawl(**self.crawl_query)
		return data

	def get_params(self):
		q= json.dumps(self.request_query)
		return re.findall('[{{](\w+)[}}]', q)

	def set_params(self, **params):
		query = json.dumps(self.request_query)
		for key, val in params.items():
			if val != '':
				query = query.replace(val, '{{%s}}' % key)
		self.request_query = json.loads(query)
		self.parameters = params.keys()
		return self.get_params()

	def save(self, name, description):
		val = {
			'name':name,
			'description':description,
			'saved_at':datetime.now().strftime('%Y-%m-%d %H:%M'),
			'request_query':self.request_query,
			'handle_query':self.handle_query,
			'crawl_query':self.crawl_query,
			'grabber':self.grabber,
			'freshness':self.freshness,
			'handler':self.handler
		}
		with open('%s/%s.json' % (config.query_lib, name), 'wb') as f:
			json.dump(val, f)



class SavedQuery(Query):
	def __init__(self,  name=None, request = None, handle= None):
		if name != None:
			with open('%s/%s.json' % (config.query_lib, name), 'rb') as f:
				q= json.load(f)
		self.name = name
		self.description = q['description']
		self.freshness = q['freshness']
		self.grabber = q['grabber']
		self.handler = q['handler']
		self.handle_query = q['handle_query']
		self.request_query = q['request_query']
		self.crawl_query = q['crawl_query']
