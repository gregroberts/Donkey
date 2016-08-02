from donkey import handler
import json



def test_JMESPATH_BASIC():
	gg = {'a':'b', 'b':'c'}
	assert handler.handle('JMESPATH',gg,'a') == 'b'
	assert handler.handle('JMESPATH',gg,'b') == 'c'

def test_XPATH_HANDLER_BASIC():
	gg = '<html><title>YAY</title></html>'
	r = handler.handle('XPATH',gg, '//title//text()')
	assert r == ['YAY']


if __name__ == '__main__':
	print handlers.__dict__