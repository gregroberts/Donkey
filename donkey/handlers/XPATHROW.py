from lxml import etree


def clean(res):
	if isinstance(res, basestring):
		return res.strip().replace('\n',' ')
	elif isinstance(res, list):
		if len(res)>0 and not isinstance(res[0], basestring):
			if any(map(lambda x: type(x)==etree._Element, res)):
				return res
		stuff = filter(lambda x: bool(x), map(clean, res))
		return ','.join(stuff).strip()
	elif isinstance(res, dict):
		return {i:clean(j) for i, j in res.items()}
	else:
		return res


class handler:
	def __init__(self):
		pass

	def parse(self, data):
		return etree.HTML(data.replace('&quot;','').encode('ascii', errors = 'ignore'))

	def query(self, obj, querystr):
		if isinstance(obj, list):
			res = [clean(i.xpath(querystr)) for i in obj]
		else:
			res = obj.xpath(querystr)
			return clean(res)


info = {
	'name':'XPathRow',
	'short_description':'For doing Xpath queries and returning only one result!',
	'long_description':'''lxml is great and all, but most of the time, we just want one result per cell.
The XPathRow Handler does this for us. Whatever lxml returns, gets flattened and concatenated into a string.
The exception is when the query returns an element. This is returned as a list of elements as per the spec.
This allows you to continue using subqueries, and still return tabular data.''',
	'url':'http://lxml.de'
}