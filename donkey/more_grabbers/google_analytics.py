import apiclient
from . import config

from httplib2 import Http

def grabber(kwargs):
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
	kwargs['ids'] = kwargs.get('ids',viewid)
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


info = {
	'name':'google_analytics',
	#a brief outline of what it does
	'short_description':'For interacting with the Google Analytics API',
	#a longer explanation of what it does and how it can be used
	'long_description':'''This wraps the Google API Client Library for Python.
Takes care of the Oauth2 Signed Credentials stuff.
The form of the data returned by the wrapped library is kinda weird,
so this grabber changes it to be a dict with headers for each row.
Also returns a bit of metadata.
An important point to note, is that wherever the API docs state a parameter with a '-'
these must be replaced with an underscore (because of how Donkey operates).
Setup requires a service account. See instructions at:  https://developers.google.com/analytics/devguides/reporting/core/v4/quickstart/service-py
the private key file for the account must be stated in the config.
Also, you may supply a view id in the params, but you should also specify a default view id in the config.
There's bloody loads of optional parameters!!!!
''',
	#the kwargs which MUST be present for a successful grab
	'required_parameters':{
		'start_date':'the start date (%y-%m-%d) for the data you want returned',
		'end_date':'the end date (%y-%m-%d) for the data you want returned',
		'metrics':'the metrics you want to see. (see the url for further details)',
	},
	'optional_parameters':{
	},
	'url':'https://developers.google.com/analytics/devguides/reporting/core/dimsmets'
}