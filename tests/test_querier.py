from donkey import querier

def test_querier_basic_requests_xpath():
	test2 = {
		'request':{
			'url':'http://example.com'
		},
		'handle':{
			'title':'//title//text()'
		}	}
	assert querier.query(test2)['title'] == ['Example Domain']


def notest_querier_advanced_twitter_jmespath_crawl():
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
		'max':2
		}
	}
	gg = querier.query(test1)[0].keys()
	assert gg == ['text']



def notest_querier_advanced_requests_xpath_crawl():
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
	gg = querier.query(test3)
	assert type(gg) is type([]) and len(gg) > 0
