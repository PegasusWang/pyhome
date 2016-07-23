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
import requests
from functools import wraps
from random import randint
from tld import get_tld
from config.config import CONFIG


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


def retry(retries=3, sleep=CONFIG.CRAWLER.SLEEP):
    """一个失败请求重试，或者使用下边这个功能强大的retrying
    pip install retrying
    https://github.com/rholder/retrying

    :param retries: number int of retry times.
    """
    def _retry(func):
        @wraps(func)
        def _wrapper(*args, **kwargs):
            index = 0
            while index < retries:
                index += 1
                try:
                    response = func(*args, **kwargs)
                    if response.status_code == 404:
                        print(404)
                        break
                    elif response.status_code != 200:
                        print(response.status_code)
                        change_ip()
                        continue
                    else:
                        break
                except Exception as e:
                    traceback.print_exc()
                    print('change ip')
                    response = None
                    change_ip()

                if sleep is not None:
                    time.sleep(sleep*index + randint(1, 10))

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


def logged(class_):
    """logged decorator.

    :param class_: add 'logger' attribute to class
    """
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    class_.logger = logging.getLogger(class_.__name__)
    return class_
