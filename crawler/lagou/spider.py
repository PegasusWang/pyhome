#!/usr/bin/env python
# -*- coding:utf-8 -*-


import _env
from extract import extract_all
from lib._db import get_db
from utils import UrlManager
from web_util import parse_curl_str, change_ip, get


class T(object):
    curl_str = """"""
    db = get_db('htmldb')
    col = getattr(db, 'lagou_html')    # collection
    sleep = None

    def __init__(self, domain):
        self.domain = domain
        self.url_manager = UrlManager(domain)

    def add_url(self, url):
        self.url_manager.add_url(url)

    def get_response(self, url, **kwargs):
        _, headers, _ = parse_curl_str(self.curl_str)
        return get(url, headers=headers, **kwargs)

    def url_nums(self):
        return self.url_manager.url_nums()

    def next_url(self, inorder=True):
        if inorder:
            return self.url_manager.first_url()
        else:
            return self.url_manager.last_url()

    def remove_url(self, url):
        return self.url_manager.remove_url(url)

    def save_html(self, html):
        # mongo 判断重复
        pass

    def run(self):
        # 重试；入库；移除url；换ip, sleep
        pass


if __name__ == '__main__':
    pass
