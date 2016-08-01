#!/usr/bin/env python
# -*- coding:utf-8 -*-


import _env
import json
import re
from bs4 import BeautifulSoup
from html_parser import Bs4HtmlParser

from lib._db import get_db


class LagouHtmlParser(Bs4HtmlParser):
    """HtmlParser 解析lagou网页内容"""

    db = get_db('')    # TODO assign a db
    col = getattr(db, '')    # TODO assign a collection
    pat = re.compile(r'[\n\r\t]')


    def parse(self):
    # TODO 职位信息的获取，定义好字段
        pass

if __name__ == '__main__':
    pass
