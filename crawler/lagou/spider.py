#!/usr/bin/env python
# -*- coding:utf-8 -*-


import _env
import random
import time
import traceback
import requests
from pprint import pformat
from functools import wraps
from requests.exceptions import TooManyRedirects, Timeout

from config.config import CONFIG
from extract import extract_all
from lib._db import get_db
from utils import UrlManager, IncrId
from web_util import (
    change_ip, logged, cookie_dict_from_cookie_str, CurlStrParser,
)


def retry(retries=CONFIG.CRAWLER.RETRY or 5, sleep=CONFIG.CRAWLER.SLEEP,
          changeip=False):
    """一个失败请求重试，或者使用下边这个功能强大的retrying
    pip install retrying
    https://github.com/rholder/retrying
    文章：常见的爬虫策略
    http://mp.weixin.qq.com/s?__biz=MzAwMDU1MTE1OQ==&mid=2653547274&idx=1&sn=52e5037b163146c1656eedce2da1ecd8&scene=1&srcid=0527MEXhNRZATtlTPhinD5Re#rd

    :param retries: number int of retry times.
    301 Moved Temporarily
    401 Unauthorized
    403 Forbidden
    404 Not Found
    408 Request Timeout
    429 Too Many Requests
    503 Service Unavailable
    """
    def _retry(func):
        @wraps(func)
        def _wrapper(*args, **kwargs):
            index = 0
            while index < retries:
                index += 1
                try:
                    response = func(*args, **kwargs)
                    if response and (
                        LagouCrawler.is_block_html(response.text) or
                        LagouCrawler.is_check_html(response.text)
                    ):
                        sleep_time = (sleep ** index + random.randint(1, 10))
                        if sleep_time > 300:   # 5 mins
                            change_ip()
                            continue
                        else:
                            print('sleep for %ds' % sleep_time)
                            time.sleep(sleep_time)
                            continue

                    if response.status_code in (301, 302, 404, 500):
                        print('status_code', response.status_code)
                        break
                    elif response.status_code != 200:
                        print(response.status_code)
                        if changeip:
                            change_ip()
                        continue
                    else:
                        break
                except Exception as e:
                    traceback.print_exc()
                    response = None
                    if isinstance(e, Timeout):
                        if sleep is not None:
                            time.sleep(sleep + random.randint(10, 15))
                        continue
                    elif isinstance(e, TooManyRedirects):
                        break

            return response
        return _wrapper
    return _retry


_get = requests.get    # 防止循环引用


@retry(5)
def get(*args, **kwds):
    kwds.setdefault('timeout', 10)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
    }
    kwds.setdefault('headers', headers)
    return _get(*args, **kwds)


@logged
class LagouCrawler(object):
    curl_str = """
    curl 'http://www.lagou.com/activityapi/icon/showIcon.json?callback=jQuery11130673730597542487_1469756732278&type=POSITION&ids=2034591%2C2147192%2C1899225%2C2112714%2C1993280%2C2107221%2C1980427%2C959204%2C1570458%2C1382996%2C2164841%2C1535725%2C2015991%2C1909703%2C1924731%2C1924585%2C1917417%2C1961327%2C1949207%2C1949217%2C1961114%2C1962767%2C1915882%2C1958811%2C1929575%2C1929708%2C1926524%2C1914752&_=1469756732279' -H 'Cookie: ctk=1469756728; JSESSIONID=006FA63ABE28DD910325F0A2B21D80DD; LGMOID=20160729094529-D8AB7E5EBC00B32D65F29DC499FDEEE0; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1469756733; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1469756733' -H 'X-Anit-Forge-Code: 0' -H 'Accept-Encoding: gzip, deflate, sdch' -H 'Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4' -H 'User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36' -H 'Accept: text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01' -H 'Referer: http://www.lagou.com/' -H 'X-Requested-With: XMLHttpRequest' -H 'Connection: keep-alive' -H 'X-Anit-Forge-Token: None' --compressed
    """
    base_url = CurlStrParser(curl_str).get_url()
    headers = CurlStrParser(curl_str).get_headers_dict()
    db = get_db('htmldb')
    col = getattr(db, 'lagou_html')    # collection
    sleep = 10

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

    @staticmethod
    def is_block_html(html, verbose=True):
        if verbose:
            print('block页面')
        return 'blocked_404' in html

    @staticmethod
    def is_check_html(html, verbose=True):
        if verbose:
            print('验证码页面')
        return '访问验证-拉勾网' in html

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
            if self.sleep:
                time.sleep(self.sleep + random.randint(1, 5))

            url = self.next_url()
            if url is not None:
                r = self.get_response(url)
                if not r:
                    self.delay_url(url)
                    self.update_headers()
                    continue

                html = r.text
                if self.is_block_html(html) or self.is_check_html(html):
                    self.delay_url(url)
                    self.update_headers()
                    continue
                else:
                    self.save_html(url, html)
                    self.remove_url(url)


def main():
    lagou_crawler = LagouCrawler('lagou.com')
    lagou_crawler.run()


if __name__ == '__main__':
    main()
