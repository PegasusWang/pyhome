#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""文章提取，从一些常见的技术博客网站提取文章内容并转成markdown输出，
用于转载"""


import html2text
import requests
import sys
from bs4 import BeautifulSoup


def html2markdown(html):
    if not html:
        return html
    markdown = html2text.html2text(html)
    return markdown


def codingpy_to_markdown(url):
    """http://codingpy.com"""
    if not url:
        return
    html = requests.get(url).text
    soup = BeautifulSoup(html)
    content = soup.find(class_='article-content')
    print(html2markdown(unicode(content)))


def main():
    try:
        url = sys.argv[1]
    except IndexError:
        url = ''
    codingpy_to_markdown(url)


if __name__ == '__main__':
    main()
