from BaseCrawler import BaseCrawler


class TestCrawler(BaseCrawler):
	def __init__(self, *args):
		print 'yay, you instantiated a crawler!'

	def _get(self, location):
		return {
			'location':location,
			'data':'response'
		}

	def _query(self, obj, query):
		if type(query) is int:
			return obj['data'][query]
		else:
			return 'query needs to be an integer'


