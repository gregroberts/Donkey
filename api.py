from flask import Flask, request, Response
from flask.ext.classy import FlaskView, route
from Scraper import Scrape
import json
from dicttoxml import dicttoxml


def resp(data, mimetype):
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


class V3View(FlaskView):
	def scrape(self, mime, crawler):
		base = request.args['base']
		query = json.loads(request.args['query'])
		scrape = Scrape(base, query, crawler)
		res = scrape.go()
		return resp(res,mime)

	#routes to deal with saved queries

application = Flask(__name__)
V3View.register(application)


if __name__ == '__main__':
	application.debug = True
	application.run()
