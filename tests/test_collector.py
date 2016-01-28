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

def test_collector_store():
	db = db_conn.get_dbconn()
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
	collector.collection(qry,'test', db)
	cursor = db.cursor()
	gg = cursor.execute('SELECT * from test')
	rr = cursor.fetchall()
	assert len(rr)  == gg and gg > 0


