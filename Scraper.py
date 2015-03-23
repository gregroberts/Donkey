from Crawlers.htmlxpath import crawler
from pprint import PrettyPrinter
from importlib import import_module


class Query(object):
	def __init__(self, crawler, query, base = None):
			self.crawler = crawler
			if base is not None:
				self.base = base
			else:
				self.base = self.crawler.base
			self.resp = self.execute(query)

	def ret_sub(self, new_base, new_query):
		if isinstance(new_base, basestring):
			new_base = self.crawler.get(new_base)
		new_obj = Query(self.crawler, new_query, new_base)
		return new_obj.resp

	def sub_test(self, obj):
		if obj.keys() == ['@base','@query']:
			new_base = self.crawler.query(obj['@base'], self.base)
			if isinstance(new_base, list):
				new_obj = [self.ret_sub(i, obj['@query']) for i in new_base]
			else:
				new_obj = self.ret_sub(new_base, obj['@query'])
			return new_obj
		else:
			return None

	def execute(self, query):
		q_dict = lambda x: {i : self.execute(j) for i, j in x.items()}
		q_list = lambda x: [self.execute(i) for i in x]
		if isinstance(query,dict):
			resp = self.sub_test(query) or q_dict(query)
		elif isinstance(query,list):
			resp = q_list(query)
		elif isinstance(query, basestring):
			resp = self.crawler.query(query, self.base)
		else:
			print type(query)
		return resp

class Scrape:
	def __init__(self, base, query, crawler_name = 'htmlxpath'):
		crawler = import_module('Crawlers.%s' %  crawler_name)
		self.crawler = crawler.crawler(base)
		self.query = query

	def go(self):
		query = Query(self.crawler, self.query)
		return query.resp




if __name__ == '__main__':
#BASIC TEST
	query = {
		"t":'//title//text()',
		"f":{
			"@base":"//ul[1]//a/@href",
			"@query":{
				"title":"//title//text()",
				"links":{
					"@base":"//a",
					"@query":{
						"text":".//text()"
					}
				}	
			}
		}
	}
#	lxml = crawler('http://lxml.de')
#	a = Query(lxml, query)
	pp = PrettyPrinter()
#	pp.pprint(a.resp)
#SCRAPER TEST
	gg = Scrape('http://lxml.de',query, 'htmlxpath')
	pp.pprint(gg.go())