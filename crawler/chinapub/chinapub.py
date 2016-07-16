#!/usr/bin/env python
# -*- coding:utf-8 -*-

import _env
import cchardet
from bs4 import BeautifulSoup
from async_spider import AsySpider
from web_util import parse_curl_str
try:
    from urllib import urlencode, quote, unquote  # py3
except ImportError:
    from urllib.parse import urlparse, quote, urlencode, unquote  # py3

"""筛选china-pub.com图书脚本"""


def to_unicode(unknow_bytes):
    """对未知编码的字节串转为unicode"""
    encoding = cchardet.detect(unknow_bytes)['encoding']
    return unknow_bytes.decode(encoding)


def get_encoding(data):
    """得到编码，得到以后直接把编码传进去，不要重复调用此函数，耗时"""
    return cchardet.detect(data)['encoding']


def convert_encoding(data, new_coding='UTF-8'):
    encoding = cchardet.detect(data)['encoding']
    if new_coding.upper() != encoding.upper():
        data = data.decode(encoding, data).encode(new_coding)
    return data


def get_header_dict():
    china_str = """curl 'http://search.china-pub.com/search/getpanicbuy.aspx?key=qg' -H 'Accept-Encoding: gzip, deflate, sdch' -H 'Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36' -H 'Accept: */*' -H 'Referer: http://search.china-pub.com/s/?key1=%bc%c6%cb%e3%bb%fa%cc%d8%bc%db&pz=1&type=59&page=1' -H 'Cookie: ASP.NET_SessionId=iagt3kbcxj1fjx55ex0gns55; __utmz=268923182.1460293356.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); CViewProductHistory=; selecthistory=%bc%c6%cb%e3%bb%fa%cc%d8%bc%db%7c%cc%d8%bc%db%ca%e9; Hm_lvt_c68f8a95996223c018465c5143d0bdea=1460293359; Hm_lpvt_c68f8a95996223c018465c5143d0bdea=1460293389; __utma=268923182.187256519.1460293356.1460293356.1460293356.1; __utmc=268923182; __utmb=268923182.5.10.1460293356; ordercount=0; cartbooknum=0; hurl=%2Cw/%2Cs/%25cc%25d8%25bc%25db%25ca%25e9%26type%3D%26pz%3D1%2Cs/%25bc%25c6%25cb%25e3%25bb%25fa%25cc%25d8%25bc%25db%26type%3D%26pz%3D1%2Cs/%25bc%25c6%25cb%25e3%25bb%25fa%25cc%25d8%25bc%25db%26pz%3D1%26type%3D59%2Cs/%25bc%25c6%25cb%25e3%25bb%25fa%25cc%25d8%25bc%25db%26pz%3D1%26type%3D59%26page%3D2%2Cs/%25bc%25c6%25cb%25e3%25bb%25fa%25cc%25d8%25bc%25db%26pz%3D1%26type%3D59%26page%3D1' -H 'Connection: keep-alive' -H 'If-Modified-Since: 0' -H 'Cache-Control: no-cache' --compressed"""
    _, headers, data = parse_curl_str(china_str)
    return headers


class ChinapubSpider(AsySpider):

    keyword = 'python'    # 需要挑选图书的关键字

    def fetch(self, url, **kwargs):
        headers = get_header_dict()
        return super(ChinapubSpider, self).fetch(url, headers=headers)

    def handle_html(self, url, html):
        html = html.decode('GB18030')
        print(html)
        soup = BeautifulSoup(html, 'lxml')
        tbody_list = soup.find_all('table')
        for tbody in tbody_list:
            sale = tbody.find('li', class_='result_name')
            if sale:
                name = sale.text
                print(name)
                if self.keyword in name.lower():
                    print(name)
                    print(tbody.find('a').get('href'))


if __name__ == '__main__':
    #url = "http://search.china-pub.com/s/?key1=%bc%c6%cb%e3%bb%fa%cc%d8%bc%db&pz=1&type=59&page="
    url = "http://search.china-pub.com/s/?key1=%cc%d8%bc%db%ca%e9&type=31&page="

    urls = []
    for page in range(1, 82):
        urls.append(url+str(page))
    s = ChinapubSpider(urls)
    s.run()
