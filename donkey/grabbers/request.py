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
