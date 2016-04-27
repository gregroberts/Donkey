from lxml import etree

class handler:
	def __init__(self):
		'''This is the simplest handler, just does xpath on html'''
		pass

	def parse(self, data):
		return etree.HTML(data.replace('&quot;','').encode('ascii', errors = 'ignore'))

	def query(self, obj, querystr):
		if isinstance(obj, list):
			res = [i.xpath(querystr) for i in obj]
		else:
			res = obj.xpath(querystr)
			if type(res) == list and len(res) > 0:
				if isinstance(res[0], basestring):
					res = [i.encode('ascii', errors = 'ignore').replace('\n','') for i in res]
			elif  isinstance(res, basestring):
				res =res.encode('ascii', errors = 'ignore').replace('\n','')
		return res