from grabber import request
from handler import handle
from jmespath import search
#here we define the different possible flows one may use to fulfill data requests



#start with the obvious one that just uses request | handle
#but it is left to be extensible




def query(qry):
	'''takes a query object, which contains:
		-how to grab,
		-(how to handle)
		-(crawl instructions)
	most simple flow just has how to grab, then returns the result'''
	to_handle = qry.get('handle',None)
	try:
		to_grab = qry['request']
	except:
		raise Exception('Query has no request parameters!')
	response = request(to_grab)
	if to_handle is not None:
		handler = to_handle.pop('@handler','XPATH')
		response = handle(handler, response, to_handle)
	return response



#def crawl(res, maps, handler):
#	reponse = []
#	for i in maps:
#		val = handle(handler, res, i['element'])
#		link = eval(repr(i['link']).replace('{{element}}',val))
#
#
#def crawler(qry):
#	'''wraps query, and allows you to crawl around pages based on some rules
#		qry should contain a section called crawl, which should contain:
#		-threshold : the depth to crawl. If not an integer, should be a jmespath query which will resolve to False when the job is done
#		-maps : an array of crawl rules, telling the crawler what the next page should be, and how to access it
#		Each map should contain:
#		-element: a query for the handler to execute, which returns what the next 'thing' is
#		-link: a {{formatted}} dict which is passed directly to the grabber, which will return a thing to be processed further
#	'''
#	crawl_args = qry.pop('crawl')
#	thresh = crawl_args['threshold']
#	maps = crawl_args['maps']
#	handler = qry['handle']['@handler']
#	response = []
#	init = query(qry)
#	itera = 0
#	if type(thresh) is int:
#		while itera <= thresh:





if __name__ == '__main__':
	test1 = {
	'request':{
		'freshness':0,
		'grabber':'twitter',
		'kwargs':{
			'route':'search/tweets.json',
			'params':{
				'q':'greg'
				}
			}
		}
	}
	print query(test1)
	test2 = {
		'request':{
			'grabber':'request',
			'kwargs':{
				'url':'http://example.com'
			}
		},
		'handle':{
			'@handler':'XPATH',
			'title':'//title//text()'
		}
	}
	print query(test2)