from config import *
import importlib
from copy import copy
from cache import cache_insert, cache_check


def get_grabber(grabber,get_what='grabber'):
	#try to get it from core grabbers
	try:
		g = importlib.import_module(
				'donkey.grabbers.%s' % grabber, 
			)
	except ImportError:
		try:
			g = importlib.import_module(
					'donkey.more_grabbers.%s' % grabber, 
				)
		except ImportError:
			raise Exception('Could not find grabber %s, check if it is installed?' % grabber)
	if get_what =='grabber':
		return g.grabber
	elif get_what == 'info':
		return g.info

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


def man(grabber):
	'''produces a man page for a specific grabber
		formatted in kinda markdown'''
	info = get_grabber(grabber, 'info')
	man = '''
#{name}

##{short_description}
-------------------------------

##Description
{long_description}
-------------------------------
##Required Parameters
'''
	for i,j in info['required_parameters'].items():
		man += '*'+i+'* - '+j + '\n'
	man += '''-------------------------------
##Optional Parameters
'''
	for i,j in info['optional_parameters'].items():
		man += '*'+i+'* - '+j + '\n'
	man += '''-------------------------------
For More information, see the grabbers specified url:
{url}'''
	return man.format(**info)




if __name__ == '__main__':
	print request({'url':'http://example.com'})