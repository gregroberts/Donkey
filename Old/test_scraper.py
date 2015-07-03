from Scraper import Scraper

def test_Scraper_starts_fine():
	scrape = Scraper('Test',
				{},
				'a location',
				0
				 )

def test_Scraper_Scrapes_string_fine():
	scrape = Scraper('Test',
				{},
				'a location',
				0
				 )	
	scrape.execute()

def test_Scraper_Scrapes_list_fine():
	scrape = Scraper('Test',
			{},
			'a location',
			[0,1,2]
			 )
	scrape.execute()

def test_Scraper_Scrapes_dict_fine():
	scrape = Scraper('Test',
			{},
			'a location',
			{'a':1, 'b':'2'}
			 )
	scrape.execute()


def test_Scrape_Scrape_works():
	scrape = Scraper('Test',
			{},
			'a location',
			0
			 )
	scrape.Scrape()

from RequestsCrawler import RequestsCrawler
from lxml.html import HtmlElement as el
def test_RequestCrawler_Basic_HTML_req():
	req = RequestsCrawler({})
	data = req._get('http://lxml.de/')
	assert type(data) is el



def test_RequestCrawler_basic_json():
	req = RequestsCrawler({'mime':'json'})
	data = req._get('http://ip.jsontest.com/')
	assert type(data) is dict

def test_RequestCrawler_xpath_query():
	req = RequestsCrawler({})
	data = req._get('http://lxml.de/')
	qry = req._query(data, '//title//text()')
	assert type(qry) is list


from Scraper import Scraper
def test_basic_http_scrape():
	scrape = Scraper('Requests',
				'http://lxml.de/',
				'title//text()')
	assert type(scrape.execute()) is list

def test_http_dict_scrape():
	scrape = Scraper('Requests',
				'http://ip.jsontest.com/',
				{'ip':'ip'})
	assert type(scrape.execute()) is dict