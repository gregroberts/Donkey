from config import *
from redis import Redis
from cPickle import loads, dumps
from time import time
from zlib import compress, decompress
import grabbers
import warnings
from traceback import format_exc

#connect to Redis, cache db stores cache
rd_conn = Redis(**REDIS_CONF)

def comp(obj, un = False):
	'''pickles and compresses a value to be put
		in the cache.
		if un, uncompress'''
	if obj is None:
		return None
	if un is True:
		s_val = decompress(obj)
		val = loads(s_val)
		return val
	else:
		s_val =dumps(obj)
		c_val = compress(s_val)
		return c_val

def mk_key(key):
	'''makes a cache key'''
	key = dumps(key).replace(':','') 
	return key

def cache_insert(s_key,val):
	'''puts the thing in the cache'''
	name = 'cache:%s' % s_key
	c_val = comp(val)
	mapping = {
		'ts':time(),
		'val':c_val
	}
	try:
		rd_conn.hmset(name, mapping)
		rd_conn.expire(name, 864000)
	except:
		warnings.warn('Cannot connect to redis cache', Warning)

def execute(key):
	'''executes the request'''
	which = key.pop('@grabber','request')
	kwargs = key
	how = grabbers.__dict__['%s_grabber' % which]
	val = how(kwargs)
	return val

def check_cache(key, freshness = 30):
	'''takes a request for data, serialises it,
		then checks if that key exists in the cache'''
	freshness = int(freshness)
	s_key = mk_key(key)
	try:
		val = rd_conn.hgetall('cache:%s' % s_key)
	except:
		warnings.warn('Cannot communicate with Redis Cache!', Warning)
	if val == {} or freshness ==0 or float(val['ts']) < time() - float(freshness*86400):
		#couldn't find it, or not fresh, so make it!
		try:
			ret = execute(key)
		except Exception as err:
			raise Exception(['grabber failed with traceback:',format_exc()])
	else:
		ret = comp(val['val'],True)
	cache_insert(s_key, ret)	
	return ret

def request(req):
	print req
	freshness = req.pop('@freshness', 30)
	resp = check_cache(req,freshness)
	return resp

