from grabber import request
from handler import handle
from jmespath import search
from pprint import pprint
from copy import copy
#here we define the different possible flows one may use to fulfill data requests



#start with the obvious one that just uses request | handle
#but it is left to be extensible


def handles(response, to_handle):
	t_h = copy(to_handle)
	if t_h is not None:
		handler = t_h.pop('@handler','XPATH')
		response = handle(handler, response, t_h)
		return response
	else:
		return response


def crawls(qry, to_grab, to_handle):
	'''does crawling based on a  given rule
		until either the rule does not hold or maxiter has been reached'''
	to_crawl = copy(qry['crawl'])
	iters = 1
	response = []
	try:
		nextlink = to_crawl.pop('next')
	except:
		raise Exception('Crawler needs a \'next\' parameter', [])
	rule = to_crawl.pop('rule','`true`')
	#if no rule and no max, errrorrrrrr
	maxiter = to_crawl.pop('max',10)
	crawl_kwargs = to_crawl
	raw_response = request(to_grab)
	res = handles(raw_response, to_handle)
	if type(res) == list:
		response.extend(res)
	else:
		response.append(res)
	link = handles(raw_response, nextlink)
	valid = search(rule, link)
	while valid and iters < maxiter:
		link.update(crawl_kwargs)
		pprint(link)
		raw_response = request(link)
		res = handles(raw_response, to_handle)
		link = handles(raw_response, nextlink)
		valid =  search(rule, link)
		iters += 1
		if type(res) == list:
			response.extend(res)
		else:
			response.append(res)
	return response


def query(qry):
	'''takes a query object, which contains:
		-how to grab,
		-(how to handle)
		-(crawl instructions)
	most simple flow just has how to grab, then returns the result'''
	qry = copy(qry)
	to_handle = qry.get('handle',None)
	try:
		to_grab = qry['request']
	except:
		raise Exception('Query has no request parameters!')
	if 'crawl' not in qry.keys():
		response = request(to_grab)
		return handles(response, to_handle)
	else:
		return crawls(qry, to_grab, to_handle)



if __name__ == '__main__':
	test1 = {
	'request':{
		'@freshness':0,
		'@grabber':'twitter',
		'route':'search/tweets.json',
		'q':'greg'
		},
	'handle':{
		'@handler':'JMESPATH',
		'@base':'content.statuses[]',
		'text':'text',
		},
	'crawl':{
		'next':{
			'route':'`search/tweets.json`',
			'q':'`greg`',
			'max_id':'content.statuses[-1].id',
			'@grabber':'`twitter`',
			'@handler':'JMESPATH'
			},
		'max':10
		}
	}
	pprint(query(test1))

	test2 = {
		'request':{
			'url':'http://example.com'
		},
		'handle':{
			'title':'//title//text()'
		}	}
	print query(test2)
	test3 = {
		'request':{
			'url':'http://www.amazon.com/Dancing-Cats-Creators-International-Seller/product-reviews/1452128332',		
		},
		'handle':{
			'@base':'//div[@class=\'a-section review\']',
			'title':'.//a[contains(@class,\'review-title\')]/text()',
		},
		'crawl':{
			'next':{
				'url':'//a[text()=\'Next\']/@href',	
			},
			'rule':'length(url)!=`0`',
			'domain':'http://amazon.com/'
		}	
	}
	pprint(query(test3))
