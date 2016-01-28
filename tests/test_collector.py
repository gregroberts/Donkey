from .. import collector, db_conn


def test_collection_basic_return():
	qry = {
		'query':{
			'request':{
				'@grabber':'request',
				'url':'http://www.amazon.com/product-reviews/1782160000'
			},
			'handle':{
				'reviews':{
					'@base':'//div[@class=\'a-section review\']',
					'text':'.//a[contains(@class,\'review-title\')]/text()',
					'date':'.//span[contains(@class,\'review-date\')]/text()',
					'empty':'.//span[@class=\'nonexistent\']/text()',
					'num':'.//span[contains(@class,\'alt\')]/text()'
				}

			}
		},
		'putter':{
			'table_name':'@return',
			'base':'reviews',
			'mapping':{
				'testcol':'num[0]',
				'testcol1':'empty[0]',
				'testcol2':'date[0]'
			}
		}
	}
	gg = collector.collection(qry, 'test')
	res = gg[0].keys()
	assert len(res) == 3


qry = {
	'query':{
		'request':{
			'@grabber':'request',
			'url':'http://www.amazon.com/product-reviews/1782160000'
		},
		'handle':{
			'reviews':{
				'@base':'//div[@class=\'a-section review\']',
				'text':'.//a[contains(@class,\'review-title\')]/text()',
				'date':'.//span[contains(@class,\'review-date\')]/text()',
				'empty':'.//span[@class=\'nonexistent\']/text()',
				'num':'.//span[contains(@class,\'alt\')]/text()'
			}

		}
	},
	'putter':{
		'table_name':'test',
		'base':'reviews',
		'mapping':{
			'testcol':'num[0]',
			'testcol1':'empty[0]',
			'testcol2':'date[0]'
		}
	}
}

def test_collector_store():
	db = db_conn.DB()
	collector.collection(qry,'test', db)
	rr = db.query('SELECT * from test')
	assert rr > 0

def test_setup_collection():
	db = db_conn.DB()
	req = {
		'CollectorName':'test',
		'QueueName':'low',
		'Frequency':90,
		'Input': '[{"a":1}]',
		'InputSource': 'json',
		'Archetype': qry,
		'CollectorDescription':'A Test'
	}
	res = collector.setup_collector(req, db)
	assert res == 'done'

def test_list_collectors():
	res = collector.list_collectors()
	nims = map(lambda x: x['CollectorName'], res)
	assert 'test' in nims