from config import *
from zlib import compress, decompress
import sqlite3
from cPickle import loads, dumps
from uuid import uuid1
from time import time

def get_cursor():
	cache = sqlite3.connect('cache.db')
	cursor = cache.cursor()
	cursor.execute('''
		CREATE TABLE IF NOT EXISTS cache
		(
			uuid TEXT,
			time INT,
			request TEXT,
			response LONGBLOB
		)
		 ''')
	cache.commit()
	return cursor
	
def clear_cache(since=0):
	cursor.execute('DELETE FROM cache where time < %d' % (time()-(since*86400)))
	cache.commit()


def comp(obj, un = False):
	'''pickles and compresses a value to be put
		in the cache.
		if un, uncompress'''
	if obj is None:
		return None
	if un is True:
		val = loads(str(obj))
		return val
	else:
		c_val = dumps(obj)
		return c_val


def cache_insert(s_key,val):
	'''puts the thing in the cache'''
	c_key = dumps(s_key)
	uuid = str(uuid1())
	t = time()
	c_val = comp(val)
	cursor = get_cursor()
	cursor.execute('''
		INSERT INTO cache
		VALUES
		(?, ?, ?, ?)
	''', (uuid, t, c_key, sqlite3.Binary(c_val)))
	cache.commit()



def cache_check(key, freshness = 30):
	'''takes a request for data, serialises it,
	then checks if that key exists in the cache'''
	c_key = dumps(key)
	since = time() - freshness * 86400
	cursor = get_cursor()
	cursor.execute('''
		SELECT response
		FROM cache
		where
			time > ?
		and 
			request = ?
		ORDER BY time desc
		LIMIT 1
	''', (since, c_key))
	res = cursor.fetchall()
	if len(res) == 0:
		return False
	else:
		return comp(res[0][0], True)
