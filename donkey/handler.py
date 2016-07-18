#This is the thing which fulfills requests for data.
#so it grabs stuff using a grabber
#then gets some more organised data from the result

from importlib import import_module
from copy import copy

def get_handler(handler):
	'''gets the handler you asked for
		all handlers must have a parse method
		and a query method'''
	if isinstance(handler, basestring):
		handler = import_module('handlers.%s' % handler,
								package='.'
								).handler
	return handler()


def execute(obj, query, handler):
	'''executes a query on a thing'''
	handy = lambda x: handler.query(obj, x)
	query = copy(query)

	if isinstance(query, basestring) or type(query) is int:
		result = handy(query)
	elif type(query) is list:
		result = map(handy, query)
	elif type(query) is dict:
		if '_base' in query.keys():
			base = query.pop('_base')
			new_obj = handy(base)
			if new_obj:
				result = [execute(i, query, handler) for i in new_obj]
			else:
				result = []
		elif query == {}:
			return obj
		else:
			result = {i:execute(obj, j, handler) for i, j in query.items()}
	else:
		raise Exception('QueryError: query of type %s is not valid ' % type(query))
	return result



def handle(handler, base, query):
	handler = get_handler(handler)
	base_obj = handler.parse(base)
	result = execute(base_obj, query, handler)
	return result



if __name__ == '__main__':
	obj = '''<html>
		<head>
			<title>TEST!! <b>po</b><b>sdfsdg</b></title>
		</head>
		<b>apapapap</b>
	</html>
	'''
	qry = {'thing':'//title/text()',
			'bees':{
				'_base':'//title/b',
				'else':'./text()'
			}
		}
	print handle('XPATH',obj, qry)