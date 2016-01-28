from .. import donkey


d = donkey.Donkey()


test2 = {
	'request':{
		'url':'http://example.com'
	},
	'handle':{
		'title':'//title//text()'
	}	
}


def test_query():

	res = d.query(test2)
	assert res['title'] == ['Example Domain']

def test_search():
	res = d.search('THIS THING DEFINITELY DOESNT EXISTSVSFDHGSDGDHSDS')
	assert len(res) == 0

def test_save():
	gg = d.save(test2, [], 'test_query', 'a test')
	assert gg == 'query saved successfully'

def test_fetch():
	gg = d.get('test_query')
	assert 'name' in gg.keys()

def test_execute():
	gg = d.execute('test_query', {})
	assert gg['title'] == ['Example Domain']

def test_search_succ():
	gg = d.search('test')
	assert len(gg) > 0
	assert set(gg[0].keys()) == set(['name','description',
							'required parameters',
							'query','saved at'])