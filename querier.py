from grabber import request
from handler import handle

#here we define the different possible flows one may use to fulfill data requests


#start with the obvious one that just uses request | handle
#but it is left to be extensible

def query(qry):
	'''takes a query object, which contains:
		-how to grab,
		-(how to handle)
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