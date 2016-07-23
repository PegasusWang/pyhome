#!/usr/bin/env python
# -*- coding:utf-8 -*-


import _env
import threading
import random
from pprint import pformat
from config.config import CONFIG
from extract import extract_all
from lib._db import get_db
from utils import UrlManager, IncrId
from web_util import parse_curl_str, change_ip, get, logged


@logged
class LagouCrawler(object):
    curl_str = """
    curl 'http://www.lagou.com/' -H 'Accept-Encoding: gzip, deflate, sdch' -H 'Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4' -H 'Upgrade-Insecure-Requests: 1' -H 'User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'Cache-Control: max-age=0' -H 'Cookie: user_trace_token=20160425192327-031ce0e3075345a78ae06025f639b168; LGUID=20160425192327-21b06b83-0ad8-11e6-9d60-525400f775ce; LGMOID=20160718091128-9D2BC18F3EC332504F4B811CADC8CCEB; JSESSIONID=81B1FCB20C6A9540E96A287EACB99416; ctk=1469186792; _gat=1; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1469012743,1469186784; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1469186784; _ga=GA1.2.1486841592.1461583315; LGSID=20160722192635-263d3d63-4fff-11e6-b141-5254005c3644; PRE_UTM=; PRE_HOST=; PRE_SITE=; PRE_LAND=http%3A%2F%2Fwww.lagou.com%2F; LGRID=20160722192635-263d3edb-4fff-11e6-b141-5254005c3644; index_location_city=%E5%8C%97%E4%BA%AC' -H 'Connection: keep-alive' --compressed
    """
    db = get_db('htmldb')
    col = getattr(db, 'lagou_html')    # collection

    def __init__(self, domain):
        self.domain = domain
        self.url_manager = UrlManager(domain)
        self.incr_id = IncrId(self.__class__.__name__)

    def add_url(self, url):
        self.url_manager.add_url(url)

    def add_url_list(self):
        for i in range(1, 532):
            url = 'http://www.lagou.com/upload/sitemap/xml/lagou_sitemap_%d.xml'%i
            self.logger.info('sitemap url: %s', url)
            html = self.get_response(url).text
            all_loc_url = extract_all('<loc>', '</loc>', html)
            self.logger.info('%s', pformat(all_loc_url))
            self.add_url(all_loc_url)

    def get_response(self, url, **kwargs):
        _, headers, _ = parse_curl_str(self.curl_str)
        if CONFIG.CRAWLER.USE_PROXY:
            kwargs.setdefault('proxies', CONFIG.CRAWLER.PROXIES)
        self.logger.info('now crawler: %s', url)
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
        self.logger.info('save html of url: %s', url)
        if html:
            self.col.update(
                {
                    '_id': self.incr_id.get(),
                    'url': url,
                },
                {
                    '$set': {'html': html}
                },
                upsert=True
            )

    def run(self):
        if not self.url_nums():
            self.add_url_list()

        while self.url_nums() > 0:
            url = self.next_url()
            r = self.get_response(url)
            html = r.text
            self.save_html(url, html)
            self.remove_url(url)


def periodic_change_ip():
    seconds = random.randint(30, 60)
    threading.Timer(seconds, periodic_change_ip).start()
    change_ip()


def main():
    periodic_change_ip()
    lagou_crawler = LagouCrawler('lagou.com')
    lagou_crawler.run()


if __name__ == '__main__':
    main()
