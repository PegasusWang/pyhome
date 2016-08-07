#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
chrome有个功能，对于请求可以直接右键copy as curl，然后在命令行里边用curl
模拟发送请求。现在需要把此curl字符串处理成requests库可以传入的参数格式，
http://stackoverflow.com/questions/23118249/whats-the-difference-between-request-payload-vs-form-data-as-seen-in-chrome
"""

import _env
import os
import re
import logging
import time
import traceback

import coloredlogs
import requests
from functools import wraps
from random import randint
from tld import get_tld
from requests.exceptions import TooManyRedirects, Timeout
from config.config import CONFIG
try:    # py3
    from urllib.parse import urlparse, quote, urlencode, unquote
    from urllib.request import urlopen
except ImportError:    # py2
    from urllib import urlencode, quote, unquote
    from urllib2 import urlopen
try:
    from http.cookies import SimpleCookie
except ImportError:
    from Cookie import SimpleCookie


def encode_to_dict(encoded_str):
    """ 将encode后的数据拆成dict
    >>> encode_to_dict('name=foo')
    {'name': foo'}
    >>> encode_to_dict('name=foo&val=bar')
    {'name': 'foo', 'val': 'var'}
    """

    pair_list = encoded_str.split('&')
    d = {}
    for pair in pair_list:
        if pair:
            key = pair.split('=')[0]
            val = pair.split('=')[1]
            d[key] = val
    return d


def parse_curl_str(s, data_as_dict=False):
    """Convert chrome curl string to url, headers dict and data string
    此函数用来作为单元测试中提交按钮的操作
    :param s: 右键chrome请求点击copy as curl得到的字符串。
    :param data_as_dict: if True, return data as dict
    """
    s = s.strip('\n').strip()
    pat = re.compile("'(.*?)'")
    str_list = [i.strip() for i in re.split(pat, s)]   # 拆分curl请求字符串

    url = ''
    headers_dict = {}
    data_str = ''

    for i in range(0, len(str_list)-1, 2):
        arg = str_list[i]
        string = str_list[i+1]

        if arg.startswith('curl'):
            url = string

        elif arg.startswith('-H'):
            header_key = string.split(':', 1)[0].strip()
            header_val = string.split(':', 1)[1].strip()
            headers_dict[header_key] = header_val

        elif arg.startswith('--data'):
            data_str = string

    if data_as_dict:
        data_dict = {}
        pair_list = unquote(data_str).split('&')
        for pair in pair_list:
            k, v = pair.split('=')
            data_dict[k] = v
        return url, headers_dict, data_dict
    else:
        return url, headers_dict, data_str


class CurlStrParser(object):
    def __init__(self, s):
        self.s = s

    def parse_curl_str(self, data_as_dict=False):
        s = self.s
        s = s.strip('\n').strip()
        pat = re.compile("'(.*?)'")
        str_list = [i.strip() for i in re.split(pat, s)]   # 拆分curl请求字符串

        url = ''
        headers_dict = {}
        data_str = ''

        for i in range(0, len(str_list)-1, 2):
            arg = str_list[i]
            string = str_list[i+1]

            if arg.startswith('curl'):
                url = string

            elif arg.startswith('-H'):
                header_key = string.split(':', 1)[0].strip()
                header_val = string.split(':', 1)[1].strip()
                headers_dict[header_key] = header_val

            elif arg.startswith('--data'):
                data_str = string

        if data_as_dict:
            data_dict = {}
            pair_list = unquote(data_str).split('&')
            for pair in pair_list:
                k, v = pair.split('=')
                data_dict[k] = v
            return url, headers_dict, data_dict
        else:
            return url, headers_dict, data_str

    def get_url(self):
        return self.parse_curl_str()[0]

    def get_headers_dict(self):
        return self.parse_curl_str()[1]

    def get_data(self, as_dict=False):
        return self.parse_curl_str()[2]


def doublewrap(f):
    '''
    http://stackoverflow.com/questions/653368/how-to-create-a-python-decorator-that-can-be-used-either-with-or-without-paramet
    a decorator decorator, allowing the decorator to be used as:
    @decorator(with, arguments, and=kwargs)
    or
    @decorator
    '''
    @wraps(f)
    def new_dec(*args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            # actual decorated function
            return f(args[0])
        else:
            # decorator arguments
            return lambda realf: f(realf, *args, **kwargs)

    return new_dec


def retry(retries=CONFIG.CRAWLER.RETRY or 3, sleep=CONFIG.CRAWLER.SLEEP,
          changeip=False):
    """一个失败请求重试，或者使用下边这个功能强大的retrying
    pip install retrying
    https://github.com/rholder/retrying
    文章：常见的爬虫策略
    http://mp.weixin.qq.com/s?__biz=MzAwMDU1MTE1OQ==&mid=2653547274&idx=1&sn=52e5037b163146c1656eedce2da1ecd8&scene=1&srcid=0527MEXhNRZATtlTPhinD5Re#rd

    :param retries: number int of retry times.
    301 Moved Temporarily
    401 Unauthorized
    403 Forbidden
    404 Not Found
    408 Request Timeout
    429 Too Many Requests
    503 Service Unavailable
    """
    def _retry(func):
        @wraps(func)
        def _wrapper(*args, **kwargs):
            index = 0
            while index < retries:
                index += 1
                try:
                    response = func(*args, **kwargs)
                    if response.status_code in (301, 302, 404, 500):
                        print('status_code', response.status_code)
                        break
                    elif response.status_code != 200:
                        print(response.status_code)
                        if changeip:
                            change_ip()
                        continue
                    else:
                        break
                except Exception as e:
                    traceback.print_exc()
                    response = None
                    if isinstance(e, Timeout):
                        if sleep is not None:
                            time.sleep(sleep + randint(1, 10))
                        continue
                    elif isinstance(e, TooManyRedirects):
                        break

            return response
        return _wrapper
    return _retry


_get = requests.get    # 防止循环引用


@retry(5)
def get(*args, **kwds):
    kwds.setdefault('timeout', 10)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
    }
    kwds.setdefault('headers', headers)
    return _get(*args, **kwds)

requests.get = get


def lazy_property(fn):
    attr_name = '_lazy_' + fn.__name__

    @property
    def _lazy_property(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
            return getattr(self, attr_name)
    return _lazy_property


def my_ip():
    # url = 'https://api.ipify.org?format=json'
    url = 'http://httpbin.org/ip'
    return requests.get(url).text


def my_socks5_ip():
    cmd = """curl --socks5 127.0.01:9050 http://checkip.amazonaws.com/"""
    os.system(cmd)


def form_data_to_dict(s):
    """form_data_to_dict s是从chrome里边复制得到的form-data表单里的字符串，
    注意*必须*用原始字符串r""

    :param s: form-data string
    """
    arg_list = [line.strip() for line in s.split('\n')]
    d = {}
    for i in arg_list:
        if i:
            k = i.split(':', 1)[0].strip()
            v = ''.join(i.split(':', 1)[1:]).strip()
            d[k] = v
    return d


def change_ip():
    my_socks5_ip()
    cmd = """(echo authenticate '"%s"'; echo signal newnym; echo quit) | nc localhost 9051"""%CONFIG.CRAWLER.PROXIES_PASSWORD
    print(cmd)
    os.system(cmd)
    my_socks5_ip()


change_tor_ip = change_ip


def get_domain(url):
    return get_tld(url)


@doublewrap
def logged(class_, colored=True):
    """logged decorator.

    :param class_: add 'logger' attribute to class
    """
    coloredlogs.install() if colored else None
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.basicConfig(level=logging.INFO, format='%(lineno)d %(message)s')
    class_.logger = logging.getLogger(class_.__name__)
    return class_


def cookie_dict_from_cookie_str(cookie_str):
    """cookie_dict_from_str Cookie字符串返回成dict

    :param cookie_str: cookies string
    """
    cookie = SimpleCookie()
    cookie.load(cookie_str)
    return {key: morsel.value for key, morsel in cookie.items()}


def cookie_dict_from_response(r):
    """cookie_dict_from_response 获取返回的response对象的Set-Cookie字符串
    并返回成dict

    :param r: requests.models.Response
    """
    cookie_str = r.headers.get('Set-Cookie')
    return cookie_dict_from_cookie_str(cookie_str)


def get_proxy_dict(ip, port, proxy_type='http' or 'socks5'):
    """get_proxy_dict return dict proxies as requests proxies
    http://docs.python-requests.org/en/master/user/advanced/

    :param ip: ip string
    :param port: int port
    :param proxy_type: 'http' or 'socks5'
    """
    proxies = {
        'http': '{proxy_type}://{ip}:{port}'.format(proxy_type=proxy_type, ip=ip, port=port),
        'https': '{proxy_type}://{ip}:{port}'.format(proxy_type=proxy_type, ip=ip, port=port),
    }
    return proxies


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i+n]


def tets():
    url = 'http://www.xicidaili.com/'
    r = get(url)
    assert r.status_code == 200


def sleeper(base=2, index=1, max_sleep=180):
    """ sleeper 2, 2^2, 2^3 ...  """
    sleep_time = min(base ** index, max_sleep)
    time.sleep(sleep_time)


if __name__ == '__main__':
    main()
