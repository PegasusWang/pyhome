#!/usr/bin/env python
# -*- coding:utf-8 -*-


import _env
from pprint import pformat
from config.config import CONFIG
from extract import extract_all
from lib._db import get_db
from utils import UrlManager, IncrId
from web_util import (
    parse_curl_str, change_ip, get, logged, cookie_dict_from_cookie_str,
    CurlStrParser,
)


@logged
class LagouCrawler(object):
    curl_str = """
    curl 'http://www.lagou.com/' -H 'Accept-Encoding: gzip, deflate, sdch' -H 'Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4' -H 'Upgrade-Insecure-Requests: 1' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'Cache-Control: max-age=0' -H 'Cookie: user_trace_token=20150911115414-e35eaafdf3cd430fb0a9fed4ca568273; LGUID=20150911115415-c53a987d-5838-11e5-8fa5-525400f775ce; fromsite=www.baidu.com; tencentSig=5171360768; RECOMMEND_TIP=true; login=true; unick=%E7%8E%8B%E5%AE%81%E5%AE%81-Python%E5%BA%94%E8%81%98; index_location_city=%E5%8C%97%E4%BA%AC; _qddab=3-ook47l.iqv1pglt; LGMOID=20160723102245-8C5562ED363CC3DD4E682EF0B3E5DB20; HISTORY_POSITION=2101463%2C20k-30k%2C%E8%BF%99%E9%87%8C%E7%A7%91%E6%8A%80%EF%BC%88%E5%8C%97%E4%BA%AC%E6%80%BB%E9%83%A8%EF%BC%89%2CPython%7C316311%2C20k-30k%2C%E6%B4%8B%E8%91%B1%E6%95%B0%E5%AD%A6%2CNode.js%7C14800%2C25k-40k%2C%E5%BE%AE%E5%BA%97%2C%E5%B9%BF%E5%91%8A%E7%A0%94%E5%8F%91%E5%B7%A5%E7%A8%8B%E5%B8%88%7C2105297%2C10k-20k%2C%E5%AE%89%E5%BF%83%E4%BF%9D%E9%99%A9%2Cjava%E5%B7%A5%E7%A8%8B%E5%B8%88%7C; ctk=1469448290; JSESSIONID=0B964345D9FDD72F69352A34D7442A24; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1468414371; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1469448291; _gat=1; PRE_UTM=; PRE_HOST=; PRE_SITE=; PRE_LAND=http%3A%2F%2Fwww.lagou.com%2F; _ga=GA1.2.878965075.1441943655; LGSID=20160725200452-fe5a753a-525f-11e6-b14c-5254005c3644; LGRID=20160725200458-02459914-5260-11e6-b14c-5254005c3644' -H 'Connection: keep-alive' --compressed
    """
    base_url = CurlStrParser(curl_str).get_url()
    headers = CurlStrParser(curl_str).get_headers_dict()
    db = get_db('htmldb')
    col = getattr(db, 'lagou_html')    # collection

    def __init__(self, domain):
        self.domain = domain
        self.url_manager = UrlManager(domain)
        self.incr_id = IncrId(self.__class__.__name__)

    def add_url(self, url):
        self.url_manager.add_url(url)

    def delay_url(self, url, nums=10):
        self.logger.info('delay url: %s', url)
        self.url_manager.delay_url(url, nums)

    def add_url_list(self):
        for i in range(1, 532):
            url = 'http://www.lagou.com/upload/sitemap/xml/lagou_sitemap_%d.xml'%i
            self.logger.info('sitemap url: %s', url)
            html = self.get_response(url).text
            all_loc_url = extract_all('<loc>', '</loc>', html)
            self.logger.info('%s', pformat(all_loc_url))
            self.add_url(all_loc_url)

    def update_headers(self, changeip=True):
        if changeip:
            change_ip()
        r = get(self.base_url)
        h = cookie_dict_from_cookie_str(r.headers.get('Set-Cookie'))
        cookies_dict = cookie_dict_from_cookie_str(self.headers['Cookie'])
        cookies_dict.update(h)
        self.headers['Cookie'] = cookies_dict
        self.logger.info('headers: %s', pformat(self.headers))

    def get_response(self, url, **kwargs):
        if CONFIG.CRAWLER.USE_PROXY:
            kwargs.setdefault('proxies', CONFIG.CRAWLER.PROXIES)
        self.logger.info('now crawler: %s', url)
        return get(url, headers=self.headers, **kwargs)

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

        self.update_headers()

        while self.url_nums() > 0:
            url = self.next_url()
            if url is not None:
                r = self.get_response(url)
                if not r:
                    self.delay_url(url)
                    self.update_headers()
                    continue
                html = r.text
                self.save_html(url, html)
                self.remove_url(url)


def main():
    lagou_crawler = LagouCrawler('lagou.com')
    lagou_crawler.run()


if __name__ == '__main__':
    main()
