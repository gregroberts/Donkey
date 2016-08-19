import oauth2 as oauth
import json
from urllib import urlencode
from . import config

def grabber(kwargs):
	'''kwargs must include:
		-route. e.g. 
			for https://api.twitter.com/1.1/search/tweets.json?q=%40twitterapi
			route would be search/tweets.json
		-all the other params are passed into the query string of the request
			for https://api.twitter.com/1.1/search/tweets.json?q=%40twitterapi
			paramters would be {'q':'@twitterapi'}
	'''
	atts = config.twitter
	consumer = oauth.Consumer(key = atts['consumer_key'], secret = atts['consumer_secret'])
	token = oauth.Token(key=atts['access_token'], secret = atts['access_token_secret'])
	client = oauth.Client(consumer, token)
	try:
		route = kwargs.pop('route')
	except:
		raise Exception('twitter grabber expects \'route\' parameter ')
	params = urlencode(kwargs)
	url = 'https://api.twitter.com/1.1/%s?%s' % (route , params)
	resp, content = client.request(url, "GET")
	content = json.loads(content)
	res = {
		'response':resp,
		'content': content
	}
	#TODO add exception handler
	return res
