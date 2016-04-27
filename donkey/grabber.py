from config import *
import importlib
from copy import copy
from cache import cache_insert, cache_check



def execute(grabber, kwargs):
	'''executes the request'''
	if isinstance(grabber, basestring):
		how = importlib.import_module( 'grabbers.%s' % grabber, 
										package='.'
										).grabber
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