#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re
from io import open
from collections import namedtuple
from pprint import pprint

from html_parser import Bs4HtmlParser
from web_util import get
from thread_pool_spider import ThreadPoolCrawler


class XiciHtmlParser(Bs4HtmlParser):
    # url = 'http://www.xicidaili.com/'

    fields = """country, ip, port, address, anonymous, type,
    speed, connect_time, live_time, verify_time"""
    fields_list = [i.strip() for i in fields.split(',')]
    IpInfoTag = namedtuple('IpInfo', fields)
    IpInfoText = namedtuple('IpInfoText', fields)
    pat = re.compile(r'[\n\r\t]')

    def extract_tag_default(self, tag):
        return tag.get_text()

    def extract_tag_country(self, tag):
        return tag.find('img').get('alt')

    def extract_tag_connect_time(self, tag):
        return tag.find('div').get('title')

    extract_tag_speed = extract_tag_connect_time

    def get_tags_text_from_tags(self, ip_info_tags):
        special_fileds = ['country', 'speed', 'connect_time']
        for (index, tag) in enumerate(ip_info_tags):
            tag_name = self.fields_list[index]
            if tag_name in special_fileds:
                func_name = 'extract_tag_' + tag_name
            else:
                func_name = 'extract_tag_' + 'default'
            try:
                value = getattr(self, func_name)(tag)
            except Exception as e:
                print(e)
                value = ''
            yield self.pat.sub('', value)

    def parse(self):
        table_tag = self.bs.find('table', id='ip_list')
        tr_tags = table_tag.find_all('tr')

        for tr_tag in tr_tags:
            td_tags = tr_tag.find_all('td')
            if td_tags:
                ip_info_tags = self.IpInfoTag(*td_tags)
                text_list = list(self.get_tags_text_from_tags(ip_info_tags))
                ip_info_texts = self.IpInfoText(*text_list)
                yield ip_info_texts._asdict()


class XiciCrawler(ThreadPoolCrawler):
    db = ''
    col = ''

    def init_urls(self):
        url = 'http://www.xicidaili.com/nn/%d'
        for i in range(1, 960):
            self.urls.append(url % i)

    def handle_response(self, url, response):
        if response.status_code == 200:
            html = response.text
            html_parser = XiciHtmlParser(url, html)
            ip_info_dict_list = html_parser.parse()

            self.col.update()    # TODO: save ip info to mongodb

def test():
    url = 'http://www.xicidaili.com/nn'
    # html = get(url).text
    with open('./t.html', encoding='utf-8') as f:
        html = f.read()
        x = XiciHtmlParser(url, html)
        l = list(x.parse())
        for i in l:
            print(i)


if __name__ == '__main__':
    test()
