# Donkey

Donkey is a simple but extensible web scraper.

##Installation

Install via pip:

	pip install donkey_scraper

Embarrasingly, I still don't 100% understand Pypi and distutils, especially for complex modules like lxml, so you'll need to install those dependencies seperately.

Dependencies needed:

	lxml
	jmespath

which should both be available on pip. For lxml, good luck...



##Usage

Core Donkey library covers the most simple of scraping workflows:

- perform a HTTP request
- do some kind of processing 

###Basic Usage

By default, the Query object uses the request grabber (the only one which comes as standard), and the XPATH handler.


	>>> from donkey import query
	>>> q = query.Query()
	>>> q.fetch(
	...     url='http://example.com'
	... ).handle(
	...     title = '//title//text()'
	... ).data
	0: {'title': ['Example Domain']}
	>>> 


The other standard handler is the JMESPATH handler, for querying JSON objects. Without any handling arguments, it will return the full JSON object:

	>>> q = query.Query(
	...     handler='JMESPATH'
	... )
	... q.fetch(
	...     url='http://echo.jsontest.com/insert-key-here/insert-value-here/key/value',
	... ).handle(
	... ).data
	1: {u'insert-key-here': u'insert-value-here', u'key': u'value'}
	>>> q = query.Query(
	...     handler='JMESPATH'
	... )
	... q.fetch(
	...     url='http://echo.jsontest.com/insert-key-here/insert-value-here/key/value',
	... ).handle(
	...     a='key'
	... ).data
	2: {'a': u'value'}
	>>> 

donkey caches requests in a SQLite database. How far back in the cache to look for a valid response is controlled by the freshness parameter when instanciating a query.

##Coming soon!

- More grabbers
- More handlers
- Web interface
- Automated Scraping jobs

