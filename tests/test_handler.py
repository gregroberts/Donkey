from donkey import handler

def test_handler_basic():
	obj = '''<html>
		<head>
			<title>TEST</title>
		</head>
	</html>
	'''
	qry = {'thing':'//title/text()'}
	assert handler.handle('XPATH',obj, qry)['thing'] == ['TEST']