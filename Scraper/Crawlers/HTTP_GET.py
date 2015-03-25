from requests import get as r_get
from retry import retry
from requests.exceptions import RequestException as excep


class HTTP_GET:
	@retry(excep, tries=5, delay=2, backoff=2)
	def _get(self, url, auth = None):
		if auth is not None:
			res = r_get(url, auth=auth)
		else:
			res = r_get(url)
		return res
