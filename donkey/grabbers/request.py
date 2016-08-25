import requests
from retry import retry
from urlparse import urljoin
from copy import copy

try:
	#FIX THIS AT SOME POINT, JEEZ
	requests.packages.urllib3.disable_warnings()
except:
	pass



@retry(requests.exceptions.RequestException,
		tries = 3, 
		delay = 2,
		backoff = 1)
def grabber(k):
	'''k must have at least:
		-mime
		-method
		-url
	'''	
	#have to make a copy because kwargs persists
	kwargs = copy(k)
	mime = kwargs.pop('mime','html')
	url = kwargs.pop('url')
	domain = kwargs.pop('domain',None)
	#mostly to automatically fool any bugger who returns a 503 for requests with no user agent
	if 'headers' in kwargs.keys():
		kwargs['headers']['User-agent'] = 'Donkey'
	else:
		kwargs['headers'] = {'User-agent': 'Donkey'}
	if type(url) == list:
		try:
			url =url[0]
		except:
			raise Exception('Requests error, you gave me an empty list!?')	
	if domain is not None:
		url = urljoin(domain, url)
	req = requests.request(kwargs.pop('method','get'),url,**kwargs)
	if req.status_code not in [200, 404]:
		msg = 'Request returned status code %d' % req.status_code
		raise requests.exceptions.RequestException(msg)
	if mime== 'json':
		return req.json()
	elif mime == 'html':
		return req.text.encode('ascii',errors='ignore')


info = {
	'name':'request',
	'short_description':'Wraps the Python Requests library, for basic HTTP requests',
	'long_description':'''Wraps the Python Requests library, for basic HTTP requests.
Specifically, wraps the requests.request method and returns the response.
Also implements exponential backoff for when exceptions are encountered.
The optional 'mime' parameter can be either html or json, depending on what you want to return
The optional 'method' parameter can be 'get' or 'post'. I guess you could use other verbs if you like....
Any other parameters passed to this grabber will be inserted as kwargs in the call to requests.request
''',
	'required_parameters':{
		'url':'the url you would like to request'
	},
	'optional_parameters':{
		'mime':'the mimetype you would like returned. Currently supports html (returns the text of the response) and json (calls request.json())',
		'domain':'for when you have relative links. Uses urlparse.urljoin on the url parameter to determine the domain',
		'method':'which http verb to pass to the request method',
	},
	'url':'http://docs.python-requests.org/en/master/'
}