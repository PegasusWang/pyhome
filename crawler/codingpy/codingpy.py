#!/usr/bin/env python
# -*- coding:utf-8 -*-

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
