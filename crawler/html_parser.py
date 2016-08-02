#!/usr/bin/env python
# -*- coding:utf-8 -*-


import simplejson as json
import re
from bs4 import BeautifulSoup


class Bs4HtmlParser(object):

    pat = re.compile(r'[\n\r\t]')

    def __init__(self, url, html):
        self.url = url
        self.html = self.pat.sub('', html)
        self.bs = BeautifulSoup(html)

    def parse(self):
        raise NotImplementedError()

if __name__ == '__main__':
    pass
