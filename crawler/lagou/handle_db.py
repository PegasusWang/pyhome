#!/usr/bin/env python
# -*- coding: utf-8 -*-

import _env
from pprint import pprint as pp

from lib._db import get_db
from html_parser import Bs4HtmlParser
from spider import LagouCrawler


db = get_db('htmldb')
col = getattr(db, 'lagou_html')    # collection


def test_get_db():
    o = col.find_one({'_id': 1234})
    html = o['html']
    # print html
    pp(o)


def test_get_html():
    import chardet
    _id = 46167
    o = col.find_one({'_id': _id})
    p = Bs4HtmlParser('', o['html'])
    print(p.html)
    t = p.bs.find('p', class_='msg')
    text = t.get_text()
    print(text)


def count_how_many_block_html():
    cnt = 0
    for html_doc in col.find(snapshot=True):
        html = html_doc['html']
        if LagouCrawler.is_block_html(html):
            cnt += 1
    return cnt


if __name__ == '__main__':
    test_get_html()