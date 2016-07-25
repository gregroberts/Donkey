from donkey import query

def test_querier_basic_requests_xpath():
	q = query.Query()
	test2 = {
		'request':{
			
		},
		'handle':{
			'title':'//title//text()'
		}	}
	q.fetch(url='http://example.com').handle(title='//title//text()')
	assert q.data['title'] == ['Example Domain']




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
