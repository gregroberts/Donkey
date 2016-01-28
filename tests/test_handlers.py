from .. import handlers
import json

def test_XPATH_HANDLER_BASIC():
	hand = handlers.XPATH()
	gg = '<html><title>YAY</title></html>'
	res = hand.parse(gg)
	r = hand.query(res, '//title//text()')
	assert r == ['YAY']


def test_JMESPATH_BASIC():
	hand = handlers.JMESPATH()
	gg = {'a':'b'}
	res = hand.parse(gg)
	assert hand.query(res, 'a') == 'b'
	gg2 = json.dumps(gg)
	res = hand.parse(gg2)
	assert hand.query(res, 'a') == 'b'