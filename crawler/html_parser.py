#!/usr/bin/env python
# -*- coding:utf-8 -*-


import re
from bs4 import BeautifulSoup

_pat = re.compile(r'[\n\r\t]')


class Bs4HtmlParser(object):

    def __init__(self, url, html):
        self.url = url
        self.html = _pat.sub('', html)
        self.bs = BeautifulSoup(html)

    def parse(self):
        raise NotImplementedError()

if __name__ == '__main__':
    pass
