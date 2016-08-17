#!/usr/bin/env python
# -*- coding:utf-8 -*-

import _env
from pprint import pformat
from extract import extract_all
from lib._db import get_db
from thread_pool_spider import ThreadPoolCrawler


class LagouSitemap(ThreadPoolCrawler):
    db = get_db('htmldb')
    col = getattr(db, 'lagou_url')    # collection

    def get(self, url, *args, **kwargs):
        headers = {
            'User-Agent': 'mozilla/5.0 (compatible; baiduspider/2.0; +http://www.baidu.com/search/spider.html)',
        }
        return super(LagouSitemap, self).get(
            url, headers=headers, *args, **kwargs
        )

    def handle_response(self, url, response):
        """处理http响应，对于200响应码直接处理html页面，
        否则按照需求处理不同响应码"""
        self.logger.info('url:%s', url)
        if response.code == 200:
            self.handle_html(url, response.text)

    def init_urls(self):
        for i in range(1, 541):    # max is 540
            url = 'http://www.lagou.com/upload/sitemap/xml/lagou_sitemap_%d.xml'%i
            self.urls.append(url)

    def handle_html(self, url, html):
        all_loc = extract_all('<loc>', '</loc>', html)
        self.logger.info('%s', pformat(all_loc))
        self.col.insert_many([{'ur': url} for url in all_loc])


if __name__ == '__main__':
    s = LagouSitemap()
    s.run()
