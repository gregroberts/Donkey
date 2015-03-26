from flask import Flask, request, Response
from flask.ext.classy import FlaskView, route
from Scraper.Scraper import Query
import json
from dicttoxml import dicttoxml
from importlib import import_module

def resp(data, mimetype):
	if mimetype == 'dict':
		return data	
	if mimetype == 'json':
		res = json.dumps(data)
		mt = 'application/json'
	elif mimetype == 'xml':
		res = dicttoxml(data)
		mt = 'application/xml'
	return Response(
		response = res,
		status = 200,
		mimetype = mt
		)


class V3:
	def scrape(self, mime = 'dict', crawler = 'htmlxpath', base = None, query = None):
		if base is None:
			base = request.args['base']
		if query is None:
			query = json.loads(request.args['query'])
		crawler = import_module('Scraper.Crawlers.%s' %  crawler,self)
		crawler = crawler.crawler(base)		
		query = Query(crawler, query)
		res = query.resp
		return resp(res,mime)

	#routes to deal with saved queries

class V3View(V3,FlaskView):
	pass


application = Flask(__name__)
V3View.register(application)


if __name__ == '__main__':
	application.debug = True
	application.run()

