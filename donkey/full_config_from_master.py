
#web api details
#if donkey server is running under e.g. mod_wsgi, this should be where the script is located (on the server)
web_prefix = ''


default_grabber='request'
default_handler='XPATH'
default_freshness = 30


#REDIS details
REDIS_URL = None
REDIS_HOST='192.168.0.110'
REDIS_PORT=6379



#MySQL Options, for MySQL Worker to do collections
MySQL_host = '192.168.0.110'
MySQL_user = 'doug'
MySQL_passwd = 'f34dnRr8ZA'
MySQL_port = 3306
MySQL_db = 'keyworddb'

####COLLECTOR Specific Config####
#this is the name of the schema into which we put collected data
collector_schemaname = 'collector'



####GRABBER Specific Config####

#Twitter API details
twitter={
	"consumer_key" : "4v5Fd0LXowMW0e8NbwlXww",
	"consumer_secret" : "crhxrbdW1OSzOCX7y7fqrGoM70Vq64W1H6Ad3qeDbw",
	"access_token" : "1966626637-Cf7hMKRYm89oqema871hO8Aam8sFZyGmu29CVS4",
	"access_token_secret" : "2789MfU5EbBTbZldmN65KEy39VaIxinXGsWFRdr38c"	
}


#StackExchange details
stackexchange = {
	#primary app
	'access_token':"ygM36YpkU4Lj42Oo9*yymg))",
	'key':"jIzJHnLzSj7gsh33dZSUIw((",
	#secondary app
	#'access_token':"WI4Zm1YreOWCQJUz6WXTcA))",
	#'key':"7cdVI2CjjmEAIXwlbnBFVQ((",	
}


#Google Analytics details
google_analytics = {
	#location of the p12 signature
	"pkeyloc":"C:\\Anaconda\\API Project-87aa6ff5a153.p12",
	#service account associated with
	"email":"74911772579-qvptn0rgfdp4b5og1n1mfndpa68efmpr@developer.gserviceaccount.com",
	#view with which to associate queries
	"viewid":"ga:413585"
}


#Crawlera details
crawlera = {
	"apikey":"5f9fedbd11814f9d8c8ec2ec15af28d1",
	"proxies":{"https": "https://proxy.crawlera.com:8010/"},
	"certificate":"C:\\Users\\gregr.PACKTPUB\\Documents\\crawleraCA.crt"

}