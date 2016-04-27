from donkey import handlers
import json



def test_JMESPATH_BASIC():
	hand = handlers.JMESPATH.handler()
	gg = {'a':'b'}
	res = hand.parse(gg)
	assert hand.query(res, 'a') == 'b'
	gg2 = json.dumps(gg)
	res = hand.parse(gg2)
	assert hand.query(res, 'a') == 'b'

def test_XPATH_HANDLER_BASIC():
	hand = handlers.XPATH.handler()
	gg = '<html><title>YAY</title></html>'
	res = hand.parse(gg)
	r = hand.query(res, '//title//text()')
	assert r == ['YAY']


if __name__ == '__main__':
	print handlers.__dict__