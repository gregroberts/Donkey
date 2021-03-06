from json import loads
from traceback import format_exc
from jmespath import search



class handler:
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



info = {
	'name':'JMESPATH handler',
	'short_description':'for querying json objects, or python dicts or similar',
	'long_description':'''JMESPath is awesome. Like json on steroids.
Seriously, it allows you to do so much manipulation, even filtering, on JSON like structures.''',
	'url':'http://jmespath.org/'
}