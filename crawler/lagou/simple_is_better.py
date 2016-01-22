#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""simple-is-better.com里的python职位筛选"""

import _env
import re
import json
import requests
from bs4 import BeautifulSoup
from async_spider import AsySpider
from web_util import parse_curl_str
from functools import wraps

job_url_list = []
JOB_URL = 'http://simple-is-better.com'
INDEX_URL = 'http://simple-is-better.com/jobs/beijing?page='


class IndexPageSpider(AsySpider):
    def handle_html(self, url, html):
        soup = BeautifulSoup(html)
        jobs_tag_list = soup.find_all('div', class_="job")
        for i in jobs_tag_list:
            _url = i.find('a').get('href')
            job_url_list.append(JOB_URL + _url)


class PositionPageSpider(AsySpider):
    def handle_html(self, url, html):
        soup = BeautifulSoup(html)
        h = soup.find(class_='detail box_x').find('h1').text
        if '海淀区' in html and 'python' in h.lower():
            print(url)


def test_index():
    urls = [INDEX_URL + str(page) for page in range(1, 42)]
    s = IndexPageSpider(urls)
    s.run()


def main():
    urls = [INDEX_URL + str(page) for page in range(1, 42)]
    s = IndexPageSpider(urls)
    s.run()
    page_s = PositionPageSpider(job_url_list)
    page_s.run()


if __name__ == '__main__':
    main()
