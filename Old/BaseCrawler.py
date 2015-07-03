from cacher import check_remote_cache, cache_resource
from importlib import import_module



def get_crawler(crawler_name):
	'''tries to import the correct crawler'''
	try:
		crawler = import_module('%sCrawler' % (crawler_name))
	except Exception, e:
		raise Exception(str(e))
	try:
		return crawler.__dict__['%sCrawler' % (crawler_name)]
	except:
		raise Exception('module should contain a class called %sCrawler(BaseCrawler)' % crawler_name)


		
###BASE CRAWLER###



class BaseCrawler:
	'''
		Defines a way to retreive a resource and implicity how to query it.
		Never called directly, only through Crawler instances.
		All child crawler instances should have:
			-a _get method which returns:
		 		-a resource which has been parsed and is ready to query
		 	-a _query method which:
		 		-executes a querystring on a resource
		 		-raises descriptive exceptions
		 		or
		 		-returns the result of the query
	'''

	cache = {}
	freshness = 0

	def check_cache(self, location):
		'''checks various places for a fresh copy of resource'''
		if type(location) is not str:
			return location
		elif location in self.cache:
			return self.cache[location]
		else:
			return check_remote_cache(location, self.freshness)

	def get(self, location):
		'''wraps the instance _get method, 
			if resource is str, it doesn't actually need collecting
			checks internal cache, then external cache,
			finally, calls get and tries to parse
		'''
		cached = self.check_cache(location)
		if cached is not None:
			return cached
		try:
			resource = self._get(location)
		except Exception as e:
			raise Exception('CrawlerError: Crawler returned %s' % e)
		cache_resource(resource)
		self.cache[location] = resource
		return resource

	def query(self, obj, query):
		try:
			return self._query(obj, query)
		except Exception as e:
			raise Exception('CrawlerError:Query failed with error - %s' % e)

