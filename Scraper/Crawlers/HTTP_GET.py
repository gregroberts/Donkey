from requests import get as r_get
from retry import retry
import requests.exceptions.RequestException as excep

@retry(excep, tries=5, delay=2, backoff=2))
def get(url, auth = None):
	if auth is not None:
		res = requests.get(url, auth=auth)
	else:
		res = requests.get(url)
	return res
