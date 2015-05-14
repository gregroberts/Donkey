from importlib import import_module



def get_crawler(crawler_name):
	'''tries to import the correct crawler'''
	try:
		crawler = import_module('%sCrawler' % (crawler_name))
	except Exception, e:
		raise Exception(str(e))
	try:
		return crawler.__dict__['%sCrawler' % (crawler_name)]
	except:
		raise Exception('module should contain a class called %sCrawler(BaseCrawler)' % crawler_name)