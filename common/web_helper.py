import requests
from pyquery import PyQuery


def url_to_pyquery(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'
    }
    rep = requests.get(url, timeout=5, headers=headers)

    py = PyQuery(rep.content)
    return py


def firefox_get_url(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'
    }
    response = requests.get(url, timeout=5, headers=headers)
    return response
