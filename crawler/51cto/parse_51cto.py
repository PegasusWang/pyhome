#!/usr/bin/env python
# -*- coding:utf-8 -*-

import requests
from bs4 import BeautifulSoup


def fetch(url):
    return requests.get(url).content.decode('gb18030').encode('utf-8')


def get_article_data(html):
    """http://developer.51cto.com/art/201512/501300.htm等类似页面提取文章
    返回数据字典
    """
    soup = BeautifulSoup(html, from_encoding='gb18030')


def main():
    pass


if __name__ == '__main__':
    print fetch(url='http://developer.51cto.com/art/201512/501300.htm')
