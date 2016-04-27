from grabber import request
from handler import handle
from jmespath import search
from copy import copy
import config
from pprint import pprint



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
		self.handle_query = None
		self.request_query = None

	def fetch(self, **qry):
		kwargs = copy(qry)
		if self.request_query == None:
			self.request_query = qry
		self.raw_data = request(self.grabber,
								self.freshness,
								kwargs)
		return self

	def handle(self, **qry):
		if self.handle_query == None:
			self.handle_query = qry
		self.data = handle(self.handler, self.raw_data, qry)
		return self.data


	def crawl(self, max_depth, next, rule = None):
		all_data = []
		qry = copy(self.request_query)
		if type(self.data) is list:
			all_data.extend(self.data)
		else:
			all_data.append(self.data)
		iters = 1
		if rule == None:
			check_rule = lambda : True
		else:
			check_rule = lambda : jmespath.search(rule, self.data)
		while iters < max_depth and check_rule(): 
			qry.update(self.handle(**next))
			_new = self.fetch(**qry).handle(**self.handle_query)
			if type(_new) is list:
				all_data.extend(_new)
			else:
				all_data.append(_new)
			iters += 1
		return all_data







if __name__ == '__main__':
	#q = Query(freshness=0)
	#q.fetch(url='http://example.com')
	#print q.handle(title='//title//text()')
	#url = 'http://www.amazon.com/books-used-books-textbooks/b/ref=sd_allcat_bo?ie=UTF8&node=283155'
	#print q.fetch(url=url
	#			 ).handle(t='./@href', _base='//a[contains(@href,\'/dp/\')]')
	q = Query('twitter', handler='JMESPATH')
	q.fetch(route='search/tweets.json', q='graphconnect'
			).handle(_base = 'content.statuses[]', text = 'text')
	next = {'max_id':'content.statuses[-1].id'}
	x=q.crawl(10, next)
	pprint(x)
