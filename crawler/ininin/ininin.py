#!/usr/bin/env python
# -*- coding: utf-8 -*-

import _env
import json
from functools import partial
from pprint import pprint

from bs4 import BeautifulSoup
import requests
from six.moves.urllib.parse import urlencode, quote

from web_util import parse_curl_str


BASE_URL = 'http://www.ininin.com/'
CURL_STR = """curl 'http://www.ininin.com/' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'Connection: keep-alive' -H 'Accept-Encoding: gzip, deflate, sdch' -H 'Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4' -H 'Upgrade-Insecure-Requests: 1' -H 'User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36' --compressed"""
GET_PRICE_CURL_STR = """curl 'http://action.ininin.com/in_quotation/get_price?ininin=BEGHFDGFECCCAEHR' -H 'Cookie: _serviceQQ=http%3A%2F%2Fwpa.b.qq.com%2Fcgi%2Fwpa.php%3Fln%3D1%26key%3DXzkzODA2MjI0N18zMjkyNjNfNDAwODYwMTg0Nl8yXw; _address=%E5%8C%97%E4%BA%AC%E5%B8%82%5E%E5%8C%97%E4%BA%AC%E5%B8%82%5E%E4%B8%9C%E5%9F%8E%E5%8C%BA; _gat=1; _ga=GA1.2.489086647.1467534150' -H 'Origin: http://www.ininin.com' -H 'Accept-Encoding: gzip, deflate' -H 'Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4' -H 'Upgrade-Insecure-Requests: 1' -H 'User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36' -H 'Content-Type: application/x-www-form-urlencoded' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'Cache-Control: max-age=0' -H 'Referer: http://www.ininin.com/product/200021.html' -H 'Connection: keep-alive' --data 'type=0&data=%5B%7B%22productId%22%3A%22200021%22%2C%22productParam%22%3A%22300g%E9%93%9C%E7%89%88%E7%BA%B8_1%E7%9B%92_90mm*54mm-%E8%A6%86%E5%93%91%E8%86%9C%22%2C%22productCount%22%3A%222%22%2C%22address%22%3A%22%E5%8C%97%E4%BA%AC%E5%B8%82%5E%E5%8C%97%E4%BA%AC%E5%B8%82%5E%E4%B8%9C%E5%9F%8E%E5%8C%BA%22%7D%5D' --compressed"""
_, HEADERS, _ = parse_curl_str(CURL_STR)
requests.get = partial(requests.get, headers=HEADERS)
_, HEADERS, _ = parse_curl_str(GET_PRICE_CURL_STR)
requests.post= partial(requests.post, headers=HEADERS)


def get_category(url=BASE_URL):
    r = requests.get(url)
    html = r.content.decode('utf-8')    # to unicode

    soup = BeautifulSoup(html, 'lxml')
    category_tag_list = soup.find_all(
        'div', id='nav_category', class_='nav_category'
    )


def get_all_product_url(url=BASE_URL):
    r = requests.get(url)
    html = r.content.decode('utf-8')    # to unicode
    soup = BeautifulSoup(html, 'lxml')
    category_tag = soup.find('div', id='nav_category')
    href_tag_list = category_tag.find_all('a')
    for href_tag in href_tag_list:
        href = href_tag.get('href')
        if href and href.startswith(r'http://www.ininin.com/product'):
            yield href


def parse_product(url):
    pass


def get_price():
    send_data = {
        'type': 0,
        'data': [{"productId":"200021","productParam":"300g铜版纸_1盒_90mm*54mm-覆哑膜","productCount":"2","address":"北京市^北京市^东城区"}],
    }
    url = 'http://action.ininin.com/in_quotation/get_price?ininin=BEGHFDGFECCCAEHR'
    #url = 'http://httpbin.org/post'
    encoded_data = urlencode(send_data)
    print(encoded_data)
    r = requests.post(url, data=encoded_data)
    # 根据headers中的content-type决定用什么提交https://imququ.com/post/four-ways-to-post-data-in-http.html#toc-3
    r = requests.post(url, data=urlencode(send_data))
    print(r.url)
    print(r.content)


def test():
    s = """curl 'http://action.ininin.com/in_quotation/get_price?ininin=BEGHFDGFECCCAEHR' -H 'Cookie: _serviceQQ=http%3A%2F%2Fwpa.b.qq.com%2Fcgi%2Fwpa.php%3Fln%3D1%26key%3DXzkzODA2MjI0N18zMjkyNjNfNDAwODYwMTg0Nl8yXw; _address=%E5%8C%97%E4%BA%AC%E5%B8%82%5E%E5%8C%97%E4%BA%AC%E5%B8%82%5E%E4%B8%9C%E5%9F%8E%E5%8C%BA; _gat=1; _ga=GA1.2.489086647.1467534150' -H 'Origin: http://www.ininin.com' -H 'Accept-Encoding: gzip, deflate' -H 'Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4' -H 'Upgrade-Insecure-Requests: 1' -H 'User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36' -H 'Content-Type: application/x-www-form-urlencoded' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'Cache-Control: max-age=0' -H 'Referer: http://www.ininin.com/product/200021.html' -H 'Connection: keep-alive' --data 'type=0&data=%5B%7B%22productId%22%3A%22200021%22%2C%22productParam%22%3A%22300g%E9%93%9C%E7%89%88%E7%BA%B8_1%E7%9B%92_90mm*54mm-%E8%A6%86%E5%93%91%E8%86%9C%22%2C%22productCount%22%3A%222%22%2C%22address%22%3A%22%E5%8C%97%E4%BA%AC%E5%B8%82%5E%E5%8C%97%E4%BA%AC%E5%B8%82%5E%E4%B8%9C%E5%9F%8E%E5%8C%BA%22%7D%5D' --compressed"""
    url, headers, data = parse_curl_str(s)
    r = requests.post(url, headers=headers, data=data)
    print(data)
    print(r.content)


if __name__ == '__main__':
    #get_category()
    l = get_all_product_url()
    #print(len(list(l)))
    get_price()
    test()
