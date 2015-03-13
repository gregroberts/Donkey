

def recurse(doc, crawler, query):
	'''This is the guy who hydrates the query.
	three possibilities:
	encounters a query object - 
		finds @base
		returns recurse(@base,crawler, @query)
	encounters a plain dict - 
		returns {i:recurse(j)}
	encounters a string - 
		assume is a query, return parse(j)
	'''
	if is_qry_obj(query):
		return handle(doc, crawler, query)
	elif isinstance(query, dict):
		return {i:recurse(doc, crawler, j) for i, j in query.items()}
	elif isinstance(query, basestring):
		return parse(doc, crawler, query)


def handle(doc, crawler, query):
	'''handles a query object
		finds whatever @base is,
		decides what to do at that point.
		could either return a node
	'''
	if doc == '@@START@@':
		#we're at the top
		actual_base = crawler.get(query['@base'])
	else:
		actual_base = crawler.query(query['@base'])
	if isinstance(actual_base, basestring):
		#it's a reference to another doc
		actual_base = crawler.get(query['@base'])
	return recurse(actual_base, crawler, query['@query'])


def is_qry_obj(obj):
	'''checks if it's a query object or not'''
	if isinstance(obj, dict):
		keys = [str(i) for i in obj.keys()]
		if keys == ['@base','@freshness']:
			return True
		else:
			return False
	else:
		return False


def parse(doc, crawler, query):
	'''smallest building block.
	Takes:
	 some kind of document (doc)
	 some kind of crawler (which has a method query)
	 & a query to execute (query).
	Returns the result, 
	or the exception thrown'''
	try:
		result = crawler.query(doc, query)
	except Exception as e:
		result = e
	return result


