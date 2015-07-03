DONKEY V3
=========

WIP web scraper & general data bus tool.

If this goes as well as it has in my MIND, it will be pretty neat and useful.

Currently, you can do this:

	>>> import sys
	... sys.path.append('...\GitHub\Donkey')
	... from api import V3
	... donk = V3()
	... query = {'title':'//title//text()'}
	... donk.scrape(mime = 'dict', crawler = 'htmlxpath', base = 'http://lxml.de/', query = query)
	0: {'title': ['lxml - Processing XML and HTML with Python']}
	>>> 

i.e. scraping with a ridiculously simply API.