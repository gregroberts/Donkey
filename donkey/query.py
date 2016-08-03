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

	def fetch(self,update = True, **qry):
		kwargs = copy(qry)
		if self.request_query == None or update:
			self.request_query = qry
		self.raw_data = grabber.request(self.grabber,
								self.freshness,
								kwargs)
		return self

	def handle(self, update=True, **qry):
		if self.handle_query == None:
			self.handle_query = qry
		self.data = handle(self.handler, self.raw_data, qry)
		return self

	def crawl(self, max_depth, next, rule = None):
		self.crawler = True
		all_data = []
		qry = copy(self.request_query)
		if type(self.data) is list:
			all_data.extend(self.data)
		else:
			all_data.append(self.data)
		iters = 1
		if rule == None:
			check_rule = lambda : len(self.data)>0
		else:
			check_rule = lambda : search(rule, self.raw_data)
		while iters < max_depth and check_rule(): 
			qry.update(self.handle(**next).data)
			_new = self.fetch(**qry).handle(**self.handle_query).data
			if type(_new) is list:
				all_data.extend(_new)
			else:
				all_data.append(_new)
			iters += 1
		return all_data

	def run(self, **kwargs):
		query = json.dumps(self.request_query)
		for key, val in kwargs.items():
			query = query.replace('{{%s}}' % key, val)
		query = json.loads(query)
		return self.fetch(False, **query).handle(False, **self.handle_query).data

	def get_params(self):
		q= json.dumps(self.request_query)
		return re.findall('[{{](\w+)[}}]', q)

	def set_params(self, **params):
		query = json.dumps(self.request_query)
		for key, val in params.items():
			query = query.replace(val, '{{%s}}' % key)
		self.request_query = json.loads(query)
		self.request_params = params.keys()
		return self.get_params()

	def save(self, name, description):
		req_q = {
			'request':copy(self.request_query),
			'handle':copy(self.handle_query)
		}
		req_q['request'].update({
			'@freshness':self.freshness,
			'@grabber':self.grabber,
		})
		req_q['handle'].update({
			'@handler':self.handler
		})
		val = {
			'name':name,
			'description':description,
			'saved_at':datetime.now().strftime('%Y-%m-%d %H:%M'),
			'query':req_q
		}
		with open('%s/%s.json' % (config.query_lib, name), 'wb') as f:
			json.dump(val, f)



class SavedQuery(Query):
	def __init__(self,  name=None, request = None, handle= None):
		if name != None:
			with open('%s/%s.json' % (config.query_lib, name), 'rb') as f:
				q= json.load(f)
			print q['description']
			query = q['query']
			request = query['request']
			handle = query['handle']

		self.freshness = request.pop('@freshness',config.default_freshness)
		self.grabber = request.pop('@grabber',config.default_grabber)
		self.handler = handle.pop('@handler',config.default_handler)
		self.raw_data = ''
		self.handle_query = handle
		self.request_query = request




if __name__ == '__main__':
	q = Query(freshness=0)
	q.fetch(url='http://example.com')
	print q.handle(title='//title//text()').data
	url = 'http://www.amazon.com'
	print q.fetch(url=url
				 ).handle(t='./@href', _base='//a[contains(@href,\'/dp/\')]').data
	print q.set_params(domain='com')
	q.save('testq','a test')
	print q.run(domain='co.uk')
	print q.run(domain='ca')
	q2 = SavedQuery('testq')
	print q2.get_params()
	print q2.run(domain='in')
	#q = Query('twitter', handler='JMESPATH')
	#q.fetch(route='search/tweets.json', q='graphconnect+greg'
	#).handle(_base = 'content.statuses[]', text = 'text')
	#next = {'max_id':'content.statuses[-1].id'}
	#x=q.crawl(10, next)
	#pprint(x)
	#q = Query('twitter', handler='JMESPATH', freshness=0)
	#q.fetch(route='search/tweets.json', q='graphconnect+greg'
	#).handle(_base = 'content.statuses[]', text = 'text')
	#next = {'max_id':'content.search_metadata.max_id'}
	#x=q.crawl(100, next, rule = 'content.search_metadata.next_results')
	#for i in x:
		#print i['text'].encode('ascii',errors='replace')
	#test2 = {
		#'request':{
			#'url':'http://{{site}}.com'
		#},
		#'handle':{
			#'title':'//title//text()'
		#}
	#}
	#x = SavedQuery(**test2)
	#print x.run(site='amazon')
	#print x.get_params()
	#print x.set_params(domain='com')
#	
	#print x.run(site='amazon',domain='co.uk')
