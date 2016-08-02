
from donkey import grabber

def test_grabber_basic():
	qry = {
		'url':'http://example.com',
		'params':{'thing':1,'other_thing':2}
	}
	gg = grabber.request('request',0,qry)
	assert gg[:2] == '<!'



if __name__ == '__main__':
	test_grabber_basic()
