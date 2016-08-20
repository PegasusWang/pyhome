#!/usr/bin/env python
# -*- coding:utf-8 -*-


import _env
import json
from bs4 import BeautifulSoup
from html_parser import Bs4HtmlParser

from lib._db import get_db


class LagouHtmlParser(Bs4HtmlParser):
    """HtmlParser 解析lagou网页内容"""

    def route(self):
        if 'gongsi' in self.url:
            self.parse_gongsi()
        elif 'job' in self.url:
            self.myparse_job()

    def parse_gongsi(self):
        """parse_gongsi"""
        raise NotImplementedError

    def myparse_job(self):
        bs = self.bs
        job_detail_dl_tag = bs.find(class_='job_detail')
        source = job_detail_dl_tag.find('div').text    # 盒子鱼英语技术部招聘
        job = job_detail_dl_tag.find('h1').get('title')  # 数据挖掘
        job_request_dd_tag = job_detail_dl_tag.find('dd', class_="job_request")
        salary, work_place, work_experience, work_edu, work_time = [
            span.text.strip() for span in job_request_dd_tag.find_all('span')
        ]
        job_attract = job_request_dd_tag.find_all('p')[1].text
        publist_date = job_request_dd_tag.find_all('p')[1].text
        print(job_request_dd_tag)
        print(job_attract)


if __name__ == '__main__':
    with open('./t.html') as f:
        p = LagouHtmlParser(url='job', html=f.read())
        p.myparse_job()
