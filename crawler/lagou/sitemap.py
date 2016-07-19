#!/usr/bin/env python
# -*- coding:utf-8 -*-

import _env
from async_spider import AsySpider
from extract import extract_all


class LagouSitemap(AsySpider):

    def init_urls(self):
        for i in range(1, 171):
        # for i in range(1, 2):
            url = 'http://www.lagou.com/upload/sitemap/xml/lagou_sitemap_%d.xml'%i
            self.urls.append(url)

    def handle_html(self, url, html):
        all_loc = extract_all('<loc>', '</loc>', html)
        res = []
        for url in all_loc:
            #if ('gongsi' in url) and ('html' in url):
            res.append(url)
        self.results.extend(res)


if __name__ == '__main__':
    s = LagouSitemap()
    s.run()
    res = s.results
    for i in set(res):
        print i
