#!/usr/bin/env python
# -*- coding:utf-8 -*-

import _env
import re
from async_spider import AsySpider
from bs4 import BeautifulSoup
from lib._db import get_collection
from tornado import gen
from config.config import CONFIG
from html2text import html2text
DB = CONFIG.MONGO.DATABASE


class CategorySpider(AsySpider):
    PAT = re.compile('http://www.ahlinux.com/python/(\d+).html')

    def handle_html(self, url, html):
        base_url = 'http://www.ahlinux.com/python/%s.html'
        id_list = re.findall(CategorySpider.PAT, html)
        url_list = [base_url % id for id in id_list]
        self.results.extend(url_list)


class ArticleSpider(AsySpider):

    def __init__(self, urls, concurrency=10, results=None, **kwargs):
        super(ArticleSpider, self).__init__(urls,
                                            concurrency, results, **kwargs)
        self.db = get_collection(DB, 'ahlinux_pyhome', 'motor')

    @gen.coroutine
    def update_doc(self, url, data_dict):
        yield self.db.update(
            {'source_url': url},
            {
                '$set': data_dict
            },
            True
        )

    @gen.coroutine
    def handle_html(self, url, html):
        print(url)
        soup = BeautifulSoup(html, 'lxml')
        title_tag = soup.find(class_='clear_div display_th')
        title = title_tag.h1.text
        brief = soup.find(class_='summary').text
        content_tag = soup.find('div', id='zth_content')
        content_tag.find('ul', class_='l_text clear_div').extract()
        content_tag.find('div', class_='clear_div page').extract()
        content = str(content_tag)
        #content = html2text(str(content_tag))    # use html
        data = {
            'title': title,
            'brief': brief,
            'content': content,
        }
        yield self.update_doc(url, data)


def test_CategorySpider():
    urls = ['http://www.ahlinux.com/python/']
    base_url = 'http://www.ahlinux.com/python/list%d.html'
    for page in range(2, 57):
        urls.append(base_url % page)
    s = CategorySpider(urls)
    s.run()
    for i in s.results:
        print(i)
    assert False


def test_ArticleSpider():
    urls = ['http://www.ahlinux.com/python/15440.html']
    s = ArticleSpider(urls)
    s.run()


def main():
    urls = ['http://www.ahlinux.com/python/']
    base_url = 'http://www.ahlinux.com/python/list%d.html'
    for page in range(2, 57):
        urls.append(base_url % page)
    s = CategorySpider(urls)
    s.run()
    article_urls = []
    for i in s.results:
        article_urls.append(i)
    print(article_urls)
    article_spider = ArticleSpider(article_urls)
    article_spider.run()


if __name__ == '__main__':
    main()
