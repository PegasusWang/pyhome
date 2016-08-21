#!/usr/bin/env python
# -*- coding:utf-8 -*-


import _env
import json
from pprint import pformat
from six import string_types
from bs4 import BeautifulSoup
from html_parser import Bs4HtmlParser
from lib._db import get_db


class LagouHtmlParser(Bs4HtmlParser):
    """HtmlParser 解析lagou网页内容"""

    def parse(self):
        if 'gongsi' in self.url:
            self.parse_gongsi()
        elif 'job' in self.url:
            self.parse_job()

    def parse_gongsi(self):
        """parse_gongsi"""
        raise NotImplementedError

    def parse_job(self):
        """parse_job
        :return: dict for lagou job html data
        """
        bs = self.bs
        assert 'job' in self.url
        print('handle: %s' % self.url)
        job_detail_dl_tag = bs.find(class_='job_detail')
        source = job_detail_dl_tag.find('div').text    # 盒子鱼英语技术部招聘
        job = job_detail_dl_tag.find('h1').get('title')  # 数据挖掘
        job_request_dd_tag = job_detail_dl_tag.find('dd', class_="job_request")
        salary, work_place, work_experience, work_edu, work_time = [
            span.text.strip() for span in job_request_dd_tag.find_all('span')
        ]
        job_attract = job_request_dd_tag.find_all('p')[1].text
        # publist_date = job_request_dd_tag.find_all('p')[1].text
        job_description_dd_tag = bs.find('dd', class_='job_bt')
        job_description = job_description_dd_tag.text

        job_company_dl_tag = bs.find('dl', class_='job_company')
        company_lagou_url = job_company_dl_tag.find('a').get('href')
        company_name = job_company_dl_tag.find('img').get('alt')

        ul_feature_tags = bs.find_all('ul', class_='c_feature')
        ul_feature_li_tag_list = ul_feature_tags[0].find_all('li')
        company_info_list = ['company_fields', 'company_people', 'company_url']
        for index, ul_tag in enumerate(ul_feature_li_tag_list):
            try:
                company_info_list[index] = ul_tag.text.split()[1]
            except IndexError:
                company_info_list[index] = ''
        company_fields, company_people, company_url = company_info_list

        company_step = ul_feature_tags[1].find('li').text.split()[1]
        print(company_step)
        try:
            company_addr_text = bs.find('div', class_='work_addr').text
            company_addr = ''.join(company_addr_text.split())    # remove blank
        except AttributeError:
            small_map_tag = bs.find('div', id='smallmap')
            company_addr = small_map_tag.find_previous('div').text

        to_save_set = frozenset([
            'source', 'job', 'salary', 'work_place', 'work_experience',
            'work_edu', 'work_time', 'job_attract', 'job_description',
            'company_lagou_url', 'company_name', 'company_fields',
            'company_people', 'company_url', 'company_step', 'company_addr',
        ])
        data = {}
        for k, v in locals().items():
            if k in to_save_set:
                if isinstance(k, string_types):
                    data[k] = v.strip()
                else:
                    data[k] = v
        data['job_url'] = self.url

        return data


if __name__ == '__main__':
    with open('./t.html') as f:
        p = LagouHtmlParser(url='http://job', html=f.read())
        data = p.parse_job()
        import pprint
        pprint.pprint(data)
