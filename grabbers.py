import requests
from retry import retry
from copy import copy
import config
from urllib import urlencode
import oauth2 as oauth
import json

@retry(requests.exceptions.RequestException,
		tries = 5, 
		delay = 2,
		backoff = 2)
def request(kwargs):
	'''kwargs must have at least:
		-mime
		-method
		-url
	'''
	#have to make a copy because kwargs persists
	k2 = copy(kwargs)
	mime = k2.pop('mime','html')
	req = requests.request(k2.pop('method','get'),k2.pop('url'),**k2)
	if mime== 'json':
		return req.json()
	elif mime == 'html':
		return req.text


def twitter(kwargs):
	'''kwargs must include:
		-route. e.g. 
			for https://api.twitter.com/1.1/search/tweets.json?q=%40twitterapi
			route would be search/tweets.json
		-params e.g 
			for https://api.twitter.com/1.1/search/tweets.json?q=%40twitterapi
			paramters would be {'q':'@twitterapi'}
	'''
	atts = config.twitter
	consumer = oauth.Consumer(key = atts['consumer_key'], secret = atts['consumer_secret'])
	token = oauth.Token(key=atts['access_token'], secret = atts['access_token_secret'])
	client = oauth.Client(consumer, token)
	params = urlencode(kwargs['params'])
	url = 'https://api.twitter.com/1.1/%s?%s' % (kwargs['route'] , params)
	resp, content = client.request(url, "GET")
	content = json.loads(content)
	res = {
		'response':resp,
		'content': content
	}
	return res



if __name__ == '__main__':
	print twitter({'route':'search/tweets.json',
			'params':{'q':'greg'}})
