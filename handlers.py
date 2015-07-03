#here is where we keep all of the different handlers
from lxml import etree


class XPATH:
	def __init__(self):
		'''This is the simplest handler, just does xpath on html'''
		pass

	def parse(self, data):
		return etree.HTML(data.replace('&quot;',''))

	def query(self, obj, querystr):
		if isinstance(obj, list):
			res = [i.xpath(querystr) for i in obj]
		else:
			res = obj.xpath(querystr)
			if type(res) == list and len(res) > 0:
				if isinstance(res[0], str):
					res = [i.encode('ascii', errors = 'replace').replace('\n','') for i in res]
			elif  isinstance(res, str) or isinstance(res, unicode):
				res = res.encode('ascii', errors = 'replace').replace('\n','')
		return res

