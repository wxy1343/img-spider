import requests
from retrying import retry
from fake_useragent import UserAgent


class Req:
    def __init__(self):
        self.req = requests.Session()

    @retry(stop_max_attempt_number=2)
    def get(self, url='', headers={}, cookies={}, timeout=10):
        self.url = url
        self.headers = headers
        self.cookies = cookies
        self.headers['user-agent'] = UserAgent().random
        self.timeout = timeout
        self.response = self.req.get(url=self.url, headers=self.headers, cookies=self.cookies, timeout=self.timeout)
        self.response.encoding = 'utf-8'
        return self.response

    @retry(stop_max_attempt_number=2)
    def post(self, url='', headers={}, cookies={}, data={}):
        self.url = url
        self.headers = headers
        self.cookies = cookies
        self.data = data
        self.headers['user-agent'] = UserAgent().random
        self.response = self.req.post(url=self.url, headers=self.headers, cookies=self.cookies, data=self.data)
        self.response.encoding = 'utf-8'
        return self.response

    def get_url(self):
        return self.url

    def set_url(self, url):
        self.url = url

    def del_url(self):
        self.url = None

    def get_headers(self):
        return self.headers

    def set_headers(self, headers):
        self.headers = headers

    def del_headers(self):
        self.headers = None

    def get_cookies(self):
        return self.req.cookies

    def set_cookies(self, cookies):
        self.req.cookies = cookies

    def del_cookies(self):
        self.req.cookies = None

    def get_response(self):
        return self.response

    def set_response(self, response):
        self.response = response

    def del_response(self):
        self.response = None

    _url = property(get_url, set_url, del_url)
    _headers = property(get_headers, set_headers, del_headers)
    _cookies = property(get_cookies, set_cookies, del_cookies)
    _response = property(get_response, set_response, del_response)
