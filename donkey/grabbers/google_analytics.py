import apiclient
from .. import config

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