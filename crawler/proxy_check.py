#!/usr/bin/env python
# -*- coding: utf-8 -*-


import _env
import re
import concurrent.futures
import requests
from pprint import pprint
from single_process import single_process

from lib._db import get_db
from thread_pool_spider import ThreadPoolCrawler
from ua import random_search_engine_ua
from web_util import (
    get, logged, change_ip, get_proxy_dict, chunks, get_requests_proxy_ip
)


@logged
class CheckXiciCralwer(ThreadPoolCrawler):
    """CheckXiciCralwer 用来测试代理的有效性，及时剔除没用的代理"""

    db = get_db('htmldb')
    col = getattr(db, 'xici_proxy')    # collection
    timeout = (10, 10)    # connect timeout and read timeout
    concurrency = 20

    def init_urls(self):
        """init_urls get all ip proxy from monggo"""
        url = 'http://www.lagou.com/'
        for ip_info in self.col.find(no_cursor_timeout=True):
            ip, port = ip_info['ip'], ip_info['port']
            if ip and port:
                self.urls.append((url, ip, port))    # tuple

    def get(self, url, proxies, timeout):
        headers = {
            'User-Agent': random_search_engine_ua()
        }
        return requests.get(
            url, proxies=proxies, timeout=timeout, headers=headers
        )

    def run_async(self):
        self.logger.info('before check %d proixes', self.col.count())

        for url_list in chunks(self.urls, 30):    # handle 100 every times
            pprint(url_list)
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.concurrency) as executor:
                future_to_url = {
                    executor.submit(
                        self.get, url, proxies=get_proxy_dict(ip, int(port)), timeout=self.timeout
                    ): (url, ip, port)
                    for (url, ip, port) in url_list
                }
                for future in concurrent.futures.as_completed(future_to_url):
                    url, ip, port = future_to_url[future]
                    try:
                        response = future.result()
                    except Exception as e:  # 之前使用的自己的get导致异常没raise
                        self.logger.info('delete proxy %s:%s', ip, port)
                        self.col.delete_one({'ip': ip, 'port': port})
                    else:
                        self.handle_response(url, response)

        self.logger.info('after check %d proixes', self.col.count())

    def handle_response(self, url, response):
        """handle_response 验证代理的合法性。通过发送简单请求检测是否超时"""
        if response:
            self.logger.info('url: %s %s', url, response.status_code)


class CheckKuaidailiCralwer(CheckXiciCralwer):
    db = get_db('htmldb')
    col = getattr(db, 'kuaidaili_proxy')    # collection


def check_proxy_xici():
    c = CheckXiciCralwer()
    c.run()


def check_proxy_kuaidaili():
    c = CheckKuaidailiCralwer()
    c.run()


@single_process
def main():
    check_proxy_kuaidaili()
    check_proxy_xici()

if __name__ == '__main__':
    main()
