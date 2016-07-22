#!/usr/bin/env python
# -*- coding:utf-8 -*-


import _env
from pprint import pformat
from config.config import CONFIG
from extract import extract_all
from lib._db import get_db
from utils import UrlManager, IncrId
from web_util import parse_curl_str, change_ip, get, logged


@logged
class LagouCrawler(object):
    curl_str = """"""
    db = get_db('htmldb')
    col = getattr(db, 'lagou_html')    # collection
    sleep = None

    def __init__(self, domain):
        self.domain = domain
        self.url_manager = UrlManager(domain)
        self.incr_id = IncrId(self.__class__.__name__)

    def add_url(self, url):
        self.url_manager.add_url(url)

    def add_url_list(self):
        # for i in range(1, 171):
        for i in range(1, 2):
            url = 'http://www.lagou.com/upload/sitemap/xml/lagou_sitemap_%d.xml'%i
            html = self.get_response(url).text
            all_loc_url = extract_all('<loc>', '</loc>', html)
            all_loc_url = all_loc_url[0:3]
            self.logger.info('%s', pformat(all_loc_url))
            self.add_url(all_loc_url)

    def get_response(self, url, **kwargs):
        _, headers, _ = parse_curl_str(self.curl_str)
        if CONFIG.CRAWLER.USE_PROXY:
            kwargs.setdefault('proxies', CONFIG.CRAWLER.PROXIES)
        return get(url, headers=headers, **kwargs)

    def url_nums(self):
        return self.url_manager.url_nums()

    def next_url(self, inorder=True):
        if inorder:
            return self.url_manager.first_url()
        else:
            return self.url_manager.last_url()

    def remove_url(self, url):
        self.logger.info('remove url: %s', url)
        return self.url_manager.remove_url(url)

    def save_html(self, url, html):
        # mongo 判断重复
        self.logger.info('save html of url: %s', url)
        self.col.update(
            {
                '_id': self.incr_id.get(),
                'url': url,
            },
            {
                '$set': {html: html}
            },
            upsert=True
        )

    def run(self):
        self.add_url_list()
        while self.url_nums() > 0:
            url = self.next_url()
            r = self.get_response(url)
            html = r.text
            self.save_html(url, html)
            self.remove_url(url)


def main():
    lagou_crawler = LagouCrawler('lagou.com')
    lagou_crawler.run()


if __name__ == '__main__':
    main()
