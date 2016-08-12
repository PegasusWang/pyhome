#!/usr/bin/env python
# -*- coding: utf-8 -*-

import _env
import json
import re
import time
from random import randint
from functools import partial
from pprint import pprint

from bs4 import BeautifulSoup
import requests
from six.moves.urllib.parse import urlencode, quote

from lib._db import get_db
from web_util import parse_curl_str


BASE_URL = 'http://www.ininin.com/'
CURL_STR = """curl 'http://www.ininin.com/' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'Connection: keep-alive' -H 'Accept-Encoding: gzip, deflate, sdch' -H 'Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4' -H 'Upgrade-Insecure-Requests: 1' -H 'User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36' --compressed"""
GET_PRICE_CURL_STR = """curl 'http://action.ininin.com/in_quotation/get_price?ininin=BEGHFDGFECCCAEHR' -H 'Cookie: _serviceQQ=http%3A%2F%2Fwpa.b.qq.com%2Fcgi%2Fwpa.php%3Fln%3D1%26key%3DXzkzODA2MjI0N18zMjkyNjNfNDAwODYwMTg0Nl8yXw; _address=%E5%8C%97%E4%BA%AC%E5%B8%82%5E%E5%8C%97%E4%BA%AC%E5%B8%82%5E%E4%B8%9C%E5%9F%8E%E5%8C%BA; _gat=1; _ga=GA1.2.489086647.1467534150' -H 'Origin: http://www.ininin.com' -H 'Accept-Encoding: gzip, deflate' -H 'Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4' -H 'Upgrade-Insecure-Requests: 1' -H 'User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36' -H 'Content-Type: application/x-www-form-urlencoded' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'Cache-Control: max-age=0' -H 'Referer: http://www.ininin.com/product/200021.html' -H 'Connection: keep-alive' --data 'type=0&data=%5B%7B%22productId%22%3A%22200021%22%2C%22productParam%22%3A%22300g%E9%93%9C%E7%89%88%E7%BA%B8_1%E7%9B%92_90mm*54mm-%E8%A6%86%E5%93%91%E8%86%9C%22%2C%22productCount%22%3A%222%22%2C%22address%22%3A%22%E5%8C%97%E4%BA%AC%E5%B8%82%5E%E5%8C%97%E4%BA%AC%E5%B8%82%5E%E4%B8%9C%E5%9F%8E%E5%8C%BA%22%7D%5D' --compressed"""
_, HEADERS, _ = parse_curl_str(CURL_STR)
requests.get = partial(requests.get, headers=HEADERS)
_, HEADERS, _ = parse_curl_str(GET_PRICE_CURL_STR)
requests.post = partial(requests.post, headers=HEADERS)


def get_all_product_url(url=BASE_URL):
    r = requests.get(url)
    html = r.content.decode('utf-8')
    soup = BeautifulSoup(html, 'lxml')

    category_tag = soup.find('div', id='nav_category')
    href_tag_list = category_tag.find_all('a')
    for href_tag in href_tag_list:
        href = href_tag.get('href')
        if href and href.startswith(r'http://www.ininin.com/product'):
            yield href


def get_price():
    send_data = {
        'type': 0,
        'data': [{"productId":"200021","productParam":"300g铜版纸_1盒_90mm*54mm-覆哑膜","productCount":"2","address":"北京市^北京市^东城区"}],
    }
    url = 'http://action.ininin.com/in_quotation/get_price?ininin=BEGHFDGFECCCAEHR'
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


def query_product_info_dict(product_id=None):
    """ query_product    此请求直接可以拿到商品信息，之前没注意到这个请求。:(

    :param product_id: int or string of product id
    :returns: data dict
    """
    assert product_id
    s = """
    curl 'http://action.ininin.com/in_product_new/query_product?product_id=200106&jsoncallback=BEHBAAHHHAEAICGV&ininin=BEHBAAHHHAEAJUUY' -H 'Accept-Encoding: gzip, deflate, sdch' -H 'Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36' -H 'Accept: */*' -H 'Referer: http://www.ininin.com/product/200106.html' -H 'Cookie: _serviceQQ=http%3A%2F%2Fwpa.b.qq.com%2Fcgi%2Fwpa.php%3Fln%3D1%26key%3DXzkzODA2MjI0N180MjM3NDhfNDAwODYwMTg0Nl8yXw; _address=%E5%8C%97%E4%BA%AC%E5%B8%82%5E%E5%8C%97%E4%BA%AC%E5%B8%82%5E%E4%B8%9C%E5%9F%8E%E5%8C%BA; _gat=1; _ga=GA1.2.973205482.1470919907' -H 'Connection: keep-alive' -H 'Cache-Control: max-age=0' --compressed
    """
    url, header_dict, data = parse_curl_str(s)
    url = re.sub('product_id=(\d+)&', 'product_id=%s&' % str(product_id), url)
    r = requests.get(url, headers=header_dict, data=data)    # keyword params
    # BEHBAAHHHAEAICGV({"result":0,"msg":"","data":{"result":0,"msg":"查询成功","productId":200021,"categoryId":39,"categoryName":"经典","productName":"“新”名片","productImg":"http://cloud.ininin.com/1453727435050.jpg","title":"“新”名片_铜版纸名片设计_铜版纸名片制作_铜版纸名片报价_云印","keywords":"铜版纸名片设计,铜版纸名片制作,铜版纸名片报价","description":"高档300克铜版纸，具有手感厚重，笔直挺括，质地密实、高白度、设计表现强特点。报价：最便宜3.5元至最贵59元/盒(100张)，多款铜版纸名片，5种可选铜版纸名片处理工艺。","pImages":"http://cloud.ininin.com/1453727455067.jpg,http://cloud.ininin.com/1453727457303.jpg,http://cloud.ininin.com/1453727459607.jpg,http://cloud.ininin.com/1453727472730.jpg,http://cloud.ininin.com/1453727468168.jpg","priceDesc":"8元/盒起","simpleDesc":"“新”名片【铜版纸】——案头常备的优质名片，满99包邮！","productDesc":"[{\"title\":\"下单流程\",\"content\":\"\u003cp style\u003d\\\"text-align: center;\\\"\u003e\u003cimg src\u003d\\\"http://cloud.ininin.com/1453727509640.jpg\\\"/\u003e\u003c/p\u003e\u003cp style\u003d\\\"text-align: center;\\\"\u003e\u003cimg src\u003d\\\"http://cloud.ininin.com/1453727519881.jpg\\\"/\u003e\u003c/p\u003e\u003cp style\u003d\\\"text-align: center;\\\"\u003e\u003cimg src\u003d\\\"http://cloud.ininin.com/1457590273025.jpg\\\"/\u003e\u003c/p\u003e\u003cp style\u003d\\\"text-align: center;\\\"\u003e\u003cimg src\u003d\\\"http://cloud.ininin.com/1470700220636.png\\\" style\u003d\\\"max-width:100%;\\\"/\u003e\u003c/p\u003e\u003cp\u003e\u003cbr/\u003e\u003c/p\u003e\u003cp\u003e\u003cbr/\u003e\u003c/p\u003e\"},{\"title\":\"产品介绍\",\"content\":\"\u003cdiv style\u003d\\\"text-align: center;\\\"\u003e\u003cimg src\u003d\\\"http://cloud.ininin.com/1453727574011.jpg\\\"/\u003e\u003c/div\u003e\"},{\"title\":\"使用场景\",\"content\":\"\"},{\"title\":\"规格参数\",\"content\":\"\"},{\"title\":\"下单须知\",\"content\":\"\"},{\"title\":\"物流说明\",\"content\":\"\"},{\"title\":\"售后服务\",\"content\":\"\"}]","baseInfoName":"材质类型_数量_成品尺寸-覆膜","preferntialInfo":"[{\"preferentialSort\":1,\"preferentialTitle\":\"优惠套餐\",\"preferentialDescription\":\"购买新名片印刷套餐，立享更多优惠\",\"preferentialLink\":\"http://design.ininin.com/category/131.html\"}]","addedServicesList":[],"params":{"300g铜版纸_1盒_90mm*54mm":{"覆膜":{"覆哑膜":1}},"300g铜版纸_2盒_90mm*54mm":{"覆膜":{"覆哑膜":1}},"300g铜版纸_5盒_90mm*54mm":{"覆膜":{"覆哑膜":1}},"300g铜版纸_10盒_90mm*54mm":{"覆膜":{"覆哑膜":1}},"300g铜版纸_20盒_90mm*54mm":{"覆膜":{"覆哑膜":1}},"300g铜版纸_40盒_90mm*54mm":{"覆膜":{"覆哑膜":1}},"300g铜版纸_100盒_90mm*54mm":{"覆膜":{"覆哑膜":1}}},"type":0,"standardType":0,"showType":0,"websiteShow":1,"homeShow":1,"homeShowIcon":1,"listShow":1,"listShowIcon":2,"minDistNum":-1,"targetId":"0","valuationMethod":0,"valuationValue":0.15,"productVariety":0}})
    content = r.content.decode('utf-8')
    content = content[content.find('(')+1: -2]
    return json.loads(content).get('data')


def _get_product_id_from_url(url='http://www.ininin.com/product/200021.html#300g铜版纸_1盒_90mm*54mm-覆哑膜'):
    """ _get_product_id_from_url
    :return: str product_id eg: 200021
    """
    return url.rsplit('/', 1)[1].split('.')[0]


_DB = get_db('ininin', client='mongo')
_COL = getattr(_DB, 'ininin_data')


def _save_mongo(url, data_dict):
    _COL.update(
        {'url': url},
        {
            '$set': data_dict
        },
        True
    )


def main():
    all_product_urls = list(get_all_product_url())
    for url in all_product_urls:
        if url:
            print('fetcing url: %s' % url)
            time.sleep(randint(5, 10))
            product_id = _get_product_id_from_url(url)
            data_dict = query_product_info_dict(product_id)
            _save_mongo(url, data_dict)


if __name__ == '__main__':
    main()
