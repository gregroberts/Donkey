import requests
from urlparse import urljoin
from copy import copy
from functools import wraps
from time import sleep
from random import randint, choice

def retry(ExceptionToCheck, tries=4, delay=3, backoff=2, logger=None):
	"""Retry calling the decorated function using an exponential backoff.

	http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
	original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

	:param ExceptionToCheck: the exception to check. may be a tuple of
		exceptions to check
	:type ExceptionToCheck: Exception or tuple
	:param tries: number of times to try (not retry) before giving up
	:type tries: int
	:param delay: initial delay between retries in seconds
	:type delay: int
	:param backoff: backoff multiplier e.g. value of 2 will double the delay
		each retry
	:type backoff: int
	:param logger: logger to use. If None, print
	:type logger: logging.Logger instance
	"""
	def deco_retry(f):
		@wraps(f)
		def f_retry(*args, **kwargs):
			mtries, mdelay = tries, delay
			while mtries > 1:
				try:
					return f(*args, **kwargs)
				except ExceptionToCheck, e:
					msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
					if logger:
						logger.warning(msg)
					else:
						print msg
					sleep(mdelay)
					mtries -= 1
					mdelay *= backoff
			return f(*args, **kwargs)

		return f_retry  # true decorator
	return deco_retry



try:
	#FIX THIS AT SOME POINT, JEEZ
	requests.packages.urllib3.disable_warnings()
except:
	pass

uas = [
	"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0",
	"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
	"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36",
	"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11) AppleWebKit/601.1.56 (KHTML, like Gecko) Version/9.0 Safari/601.1.56",
	"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/601.2.7 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.7",
	"Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
	"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0",
	"Mozilla/5.0 (Windows NT 10.0; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0",
	"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0",
	"Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:41.0) Gecko/20100101 Firefox/41.0",
	"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
	"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36",
	"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36",
	"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
]

@retry(requests.exceptions.RequestException,
		tries = 3, 
		delay = randint(3,15),
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
	sleep(randint(15,30))
	ua = choice(uas)
	print ua
	print url
	#mostly to automatically fool any bugger who returns a 503 for requests with no user agent
	if 'headers' in kwargs.keys():
		kwargs['headers']['User-agent'] = ua
	else:
		kwargs['headers'] = {'User-agent': ua}
	if type(url) == list:
		try:
			url =url[0]
		except:
			raise Exception('Requests error, you gave me an empty list!?')	
	if domain is not None:
		url = urljoin(domain, url)
	req = requests.request(kwargs.pop('method','get'),url,**kwargs)
	if 'robot check' in req.text.lower() or 'captcha' in req.text.lower():
		raise requests.exceptions.RequestException('We\'ve been rattled! Lay low')
	if req.status_code not in [200, 404]:
		msg = 'Request returned status code %d' % req.status_code
		raise requests.exceptions.RequestException(msg)
	if mime== 'json':
		return req.json()
	elif mime == 'html':
		return req.text.encode('ascii',errors='ignore')


info = {
	'name':'polite_request',
	'short_description':'Implements various features to reduce likelihood of being caught...',
	'long_description':'''Exponential backoff with a random delay interval
Each request also has a random delay interval.
A random user agent header is attached to the request.
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