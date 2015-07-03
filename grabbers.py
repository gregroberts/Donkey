import requests
from retry import retry
from copy import copy

@retry(requests.exceptions.RequestException,
		tries = 5, 
		delay = 2,
		backoff = 2)
def request(kwargs):
	#have to make a copy because kwargs persists
	k2 = copy(kwargs)
	mime = k2.pop('mime','html')
	req = requests.request(k2.pop('method','get'),k2.pop('url'),**k2)
	if mime== 'json':
		return req.json()
	elif mime == 'html':
		return req.text
