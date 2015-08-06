#here is where we keep all of the different handlers
from lxml import etree
from json import loads
from traceback import format_exc
from jmespath import search

class XPATH:
	def __init__(self):
		'''This is the simplest handler, just does xpath on html'''
		pass

	def parse(self, data):
		return etree.HTML(data.replace('&quot;',''))

	def query(self, obj, querystr):
		if isinstance(obj, list):
			res = [i.xpath(querystr) for i in obj]
		else:
			res = obj.xpath(querystr)
			if type(res) == list and len(res) > 0:
				if isinstance(res[0], str):
					res = [i.encode('ascii', errors = 'replace').replace('\n','') for i in res]
			elif  isinstance(res, str) or isinstance(res, unicode):
				res = res.encode('ascii', errors = 'replace').replace('\n','')
		return res

class JMESPATH:
	def __init__(self):
		'''this guy handles JSON stuff.'''
		pass

	def parse(self, data):
		'''ideally, this just checks if it needs to be parsed'''
		if isinstance(data, basestring):
			try:
				return loads(data)
			except:
				raise Exception(['Handler parse failed with traceback: ', format_exc()])
		else:
			return data

	def query(self, obj, querystr):
		
		if not bool(querystr):
			return obj
		else:
			try:
				return search(querystr, obj)
			except:
				raise Exception(['JMESPATH query failed with exception: ', format_exc()])
