#!/usr/bin/env python
# -*- coding:utf-8 -*-


import json
from bs4 import BeautifulSoup


class HtmlParser(object):
    """HtmlParser 解析lagou网页内容"""

    def __init__(self, url, html):
        self.url = url
        self.html = html
        self.bs = BeautifulSoup(html, 'lxml')

    # TODO 职位信息的获取，定义好字段

if __name__ == '__main__':
    pass
