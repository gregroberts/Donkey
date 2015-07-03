from BaseCrawler import BaseCrawler
import requests
from retry import retry
from lxml import html
from jmespath import search


class RequestsCrawler(BaseCrawler):
	def __init__(self, args):
		'''for making most general interweb requests''' 
		args.setdefault('http_method', 'GET')
		args.setdefault('mime', 'HTML')
		self.args = args

	def parse(self, req):
		if self.args['mime'] == 'HTML':
			res = html.fromstring(req.text)
		elif self.args['mime'] == 'json':
			res = req.json()
		return res

	@retry(requests.exceptions.RequestException,
		tries = 5, 
		delay = 2,
		backoff = 2)
	def _get(self, location):
		if self.args['http_method'] == 'GET':
			request = requests.get(location)
		elif self.args['http_method'] == 'POST':
			data = self.args['post_data']
			request = requests.post(location, data = data)
		res = self.parse(request)
		return res

	def _query(self, obj, query):
		if self.args['mime'] == 'HTML':
			return obj.xpath(query)
		elif self.args['mime'] == 'json':
			return search(query, obj)