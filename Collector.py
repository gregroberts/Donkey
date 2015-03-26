from api import V3
from pson import pathquery


def mysql_collector(params, cursor, schema, table, mapping):
	scraper = V3
	method = scraper.__dict__[params.pop('method')]
	data = method(scraper,**params)

	what, where = [], []
	for i, j in mapping.items():
		what.append(i)
		where.append(j)

	sql = '''REPLACE INTO %s.%s
			(%s)
			VALUES
			%s
		'''
	columns = [pathquery(data, i) for i in what]
	print columns
	rows = map(list, zip(*columns))
	heads = ','.join(where)
	print rows[0]
	row_str = [','.join(['\'%s\'' % j[0].replace('\'','') for j in i]) for i in rows]
	rows_str = ['(%s)' % (i) for i in row_str]
	rows_str = ','.join(rows_str)
	sttmnt = sql % (schema, table, heads, rows_str)
	cursor.execute(sttmnt)






if __name__ == '__main__':
	query = {
		"list":{
			"@base":"//li/a",
			"@query":{
				"link":"./text()",
				"link_loc":"./@href"
			}
		}
	}
	from dbapi import mdb
	db = mdb(local = True, db = 'test_gr')
	params ={'method':'scrape','mime':'dict','crawler':'htmlxpath','base':'http://lxml.de','query':query}
	mysql_collector(params, db.c,'test_gr','links',{'list.link':'name','list.link_loc':'loc'})
	db.done()