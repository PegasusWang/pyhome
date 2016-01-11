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
    """http://codingpy.com, 编程派"""
    if not url:
        return
    html = requests.get(url).text
    soup = BeautifulSoup(html)
    content = soup.find(class_='article-content')
    print(html2markdown(unicode(content)))


def iteye_to_markdown(url):
    """http://yunjianfei.iteye.com/blog/2185476"""
    if not url:
        return
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
    }
    html = requests.get(url, headers=headers).content
    soup = BeautifulSoup(html)
    content = soup.find(id='blog_content')
    print(html2markdown(unicode(content)))


def jianshu_to_markdown(url="http://www.jianshu.com/p/67fa1e2114c5"):
    """http://www.jianshu.com/p/67fa1e2114c5，简书"""
    if not url:
        return
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
    }
    html = requests.get(url, headers=headers).content
    soup = BeautifulSoup(html)
    content = soup.find('div', class_='show-content')
    print(content)


def emptysqua_re_to_markdown(url='https://emptysqua.re/blog/refactoring-tornado-coroutines/'):
    """https://emptysqua.re/blog/refactoring-tornado-coroutines/"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
    }
    html = requests.get(url, headers=headers).content
    soup = BeautifulSoup(html)
    content = soup.find('div', class_='post-content')
    print(html2markdown(unicode(content)))


def main():
    try:
        url = sys.argv[1]
    except IndexError:
        url = 'http://www.jianshu.com/p/67fa1e2114c5'
    emptysqua_re_to_markdown()


if __name__ == '__main__':
    main()
