from urllib import urlencode
import requests
from . import config

def grabber(kwargs):
	'''For accessing the stackexchange API
	kwargs must include route, other kwargs will be put into qs
	'''
	try:
		route = kwargs.pop('route')
	except:
		raise Exception('Grabber Error, You need to provide a \'route\' kwarg')
	qs = {
		'site': 'stackoverflow',
		'pagesize':100,
		'page':1,
	}
	qs.update(kwargs)
	qs.update(config.stackexchange)
	args = urlencode(qs)
	url = 'https://api.stackexchange.com/2.2/%s?%s' % (route,args)
	res = requests.get(url)
	return res.json()




info = {
	'name':'stackexchange',
	'short_description':'For interacting with the stackexchange api',
	'long_description':'''For interacting with the stackexchange api.
Wraps a requests call to the api.
The route parameter determines the route,
all other parameters will be put into the querystring of the request.
''',
	'required_parameters':{
		'route':'the route of the API you wish to call'
	},
	'optional_parameters':{
	},
	'url':'https://api.stackexchange.com/docs'
}