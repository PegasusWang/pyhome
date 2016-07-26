#!/usr/bin/env python
# -*- coding: utf-8 -*-


from web_util import get
from html_parser import Bs4HtmlParser


class XiciHtmlParser(Bs4HtmlParser):
    # url = 'http://www.xicidaili.com/'
    def parse(self):
        bs = self.bs



def main():
    url = get(url)


if __name__ == '__main__':
    pass
