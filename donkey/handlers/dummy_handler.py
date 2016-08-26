from lxml import etree

class handler:
	'''this is how a handler is defined. It is a class which exposes two methods.
	the parse method controls the logic of how to transform 
	a given piece of source data into a traversable, queryable data object'''
	def __init__(self):
		'''do any setup required here'''
		pass

	def parse(self, data):
		'''takes data, returns some kind of other data
		which may be queried by the query method'''
	

	def query(self, obj, query):
		'''this method takes an object to query,
		 and a query to execute on that object
		 should return one of:
		 - basestring
		 - list
		 - dictionary
		 for full compatibility'''


#each handler should have an info dict attached which documents what it is and how to use it briefly.

info = {
	'name':'',
	'short_description':'',
	'long_description':'',
	'url':''
}