import requests
from retry import retry
from copy import copy
import config
from urllib import urlencode
import oauth2 as oauth
import json
from urlparse import urlparse, urljoin
import apiclient
from httplib2 import Http
from urlparse import parse_qs


try:
	#FIX THIS AT SOME POINT, JEEZ
	requests.packages.urllib3.disable_warnings()
except:
	pass



@retry(requests.exceptions.RequestException,
		tries = 5, 
		delay = 2,
		backoff = 2)
def request_grabber(kwargs):
	'''kwargs must have at least:
		-mime
		-method
		-url
	'''	
	#have to make a copy because kwargs persists
	k2 = copy(kwargs)
	mime = k2.pop('mime','html')
	url = k2.pop('url')	
	domain = k2.pop('domain',None)
	if type(url) == list:
		try:
			url =url[0]
		except:
			raise Exception('Requests error, you gave me an empty list!?')	
	if domain is not None:
		url = urljoin(domain, url)
	req = requests.request(k2.pop('method','get'),url,**k2)
	#TODO - Add Exception handler for requests module
	if mime== 'json':
		return req.json()
	elif mime == 'html':
		return req.text.encode('ascii',errors='ignore')



def twitter_grabber(kwargs):
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



def stackexchange_grabber(kwargs):
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



def google_analytics_grabber(kwargs):
	'''kwargs must include all the things the API docs ask for, with the same names:
		https://developers.google.com/analytics/devguides/reporting/core/v3/coreDevguide'''
	#set up service
	atts = config.google_analytics
	viewid = atts['viewid']
	signed = apiclient.oauth2client.client.SignedJwtAssertionCredentials
	try:
		with open(atts['pkeyloc'], 'rb') as f:
			private_key = f.read()
	except:
		raise Exception('Grabber Error. coudld not find private key file. Check yer config')
	credentials = signed(atts['email'],private_key, 'https://www.googleapis.com/auth/analytics')
	http_auth =credentials.authorize(Http())
	service = apiclient.discovery.build('analytics','v3',http = http_auth)
	res = service.data().ga()
	#construct request
	kwargs['ids'] = viewid
	#params = {str(i).replace('-','_'):str(j[0]).replace('{SC}',';') for i,j in params.items() if j != ''}
	query = res.get(**kwargs).execute()
	heads = [i['name'] for i in query['columnHeaders']]
	response = {
		'query':query['query'],
		'columns': query['columnHeaders'],
		'totalResults':query['totalResults'],
		'isSampled': query['containsSampledData'],
		'data':[{heads[i]:datum for i, datum in enumerate(row)} for row in query.get('rows',[])],
	}
	return response


def get_user_agents():
	from querier import handles
	f_n = 'user_agents.json'
	try:
		with open(f_n,'rb') as f:
			user_agents = json.load(f)
	except:
		reg = requests.get('http://www.zytrax.com/tech/web/browser_ids.htm')
		user_agents = handles(reg.text,{'tt':'//p[@class=\'g-c-s\']/text()'})['tt']
		with open(f_n,'wb') as f:
			json.dump(user_agents,f)
	finally:
		reg = requests.get('http://www.zytrax.com/tech/web/browser_ids.htm')
		user_agents = handles(reg.text,{'tt':'//p[@class=\'g-c-s\']/text()'})['tt']		
	return user_agents	


import random
import time
def evil_request_grabber(kwargs):
	'''only slightly evil. 
	spoofs user agents from a very large list
	'''
	#have to make a copy because kwargs persists
	k2 = copy(kwargs)
	time.sleep(random.randint(0,10))
	mime = k2.pop('mime','html')
	url = k2.pop('url')	
	domain = k2.pop('domain',None)
	user_agents = get_user_agents()
	headers = k2.pop('headers',{})
	headers.update({'user-string':random.choice(user_agents)})
	if type(url) == list:
		try:
			url =url[0]
		except:
			raise Exception('Requests error, you gave me an empty list!?')	
	if domain is not None:
		url = urljoin(domain, url)
	req = requests.request(k2.pop('method','get'),url,headers=headers,**k2)
	#TODO - Add Exception handler for requests module
	if mime== 'json':
		return req.json()
	elif mime == 'html':
		return req.text.encode('ascii',errors='ignore')






if __name__ == '__main__':
	print twitter_grabber({'route':'search/tweets.json',
			'q':'greg'})
