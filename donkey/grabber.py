from config import *
import importlib
from copy import copy
from cache import cache_insert, cache_check


def get_grabber(grabber):
	#try to get it from core grabbers
	try:
		g = importlib.import_module(
				'donkey.grabbers.%s' % grabber, 
			).grabber
		return g
	except ImportError:
		try:
			g = importlib.import_module(
					'donkey.more_grabbers.%s' % grabber, 
				).grabber	
			return g
		except ImportError:
			raise Exception('Could not find grabber %s, check if it is installed?' % grabber)


def execute(grabber, kwargs):
	'''executes the request'''
	if isinstance(grabber, basestring):
		how = get_grabber(grabber)
		val = how(kwargs)
	else:
		val = grabber(kwargs)
	return val



def request(grabber, freshness, req):
	key = copy(req)
	resp = cache_check(req,freshness)
	if resp == False:
		resp = execute(grabber, req)
		cache_insert(key, resp)
	return resp


if __name__ == '__main__':
	print request({'url':'http://example.com'})