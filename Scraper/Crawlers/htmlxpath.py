from HTTP_GET import HTTP_GET
from lxml import etree
from urlparse import urljoin


class crawler(HTTP_GET):
	cache = {}

	def __init__(self, base):
		self.base_str = base
		self.base = self.get(base)
		
	def get(self, thing):
		thing = urljoin(self.base_str, thing)
		if thing not in self.cache.keys():
			res = self._get(thing)
			res = etree.HTML(res.content)
			self.cache[thing] = res
		else:
			res = self.cache[thing]
		return res

	def query(self, q_string, doc):
		if isinstance(doc, list):
			resp = [i.xpath(q_string) for i in doc]
		else:
			resp = doc.xpath(q_string)
		return resp