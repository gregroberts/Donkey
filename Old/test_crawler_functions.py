from BaseCrawler import get_crawler
from TestCrawler import TestCrawler

import sys




def test_crawler_methods_work():
	test = TestCrawler()
	test_response = test.get('test')
	test_query = test.query(test_response, 1)
	assert test_query == 'e'

