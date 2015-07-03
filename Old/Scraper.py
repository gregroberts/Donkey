from BaseCrawler import get_crawler

import Actions


class Scraper:
	def __init__(self, 
			 crawler_name, 
			  base,
			  query,
			   crawler_args = {},
			  freshness = 0,
			  actions = []):
		c = get_crawler(crawler_name)
		self.crawler = c(crawler_args)
		self.crawler.freshness = freshness
		self.base = self.crawler.get(base)
		self.query = query

	def _isqryobj(self,obj):
		'''tests if it has been passed a query object'''
		if type(obj) is dict:
			if obj.keys() == ('base', 'query'):
				return True
			else:
				return False
		else:
			return False

	def execute(self, base = None, query =None, ):
		'''executes a query on a thing'''
		if query is None:
			query = self.query
		if base is None:
			base = self.base
		if type(query) is str or type(query) is int:
			result = self.crawler.query(base, query)
		elif type(query) is list:
			result = [self.execute(base, i) for i in query]
		elif type(query) is dict:
			if self._isqryobj(query):
				result = self.execute(query['base'], query['query'])
			else:
				result = {i:self.execute(base, j) for i, j in query.items()}
		else:
			raise Exception('QueryError: query of type %s is not valid ' % type(query))
		return result

	def Scrape(self):
		'''does the whole scrape, performs the actions and returns it'''
		try:
			unclean = self.execute()
		except Exception as e:
			raise Exception('ScraperError: Scrape failed with exception - %s' % e)
		try:
			clean = Actions.clean(unclean)
		except Exception as e:
			raise Exception('ActionsError: Cleaning failed with exception - %s' % e)
		return clean