#!/usr/bin/env python
# -*- coding:utf-8 -*-


import json
from bs4 import BeautifulSoup

from lib._db import get_db


class HtmlParser(object):
    """HtmlParser 解析lagou网页内容"""

    db = get_db('')    # TODO assign a db
    col = getattr(db, '')    # TODO assign a collection

    def __init__(self, url, html):
        self.url = url
        self.html = html
        self.bs = BeautifulSoup(html, 'lxml')

    # TODO 职位信息的获取，定义好字段

if __name__ == '__main__':
    pass
