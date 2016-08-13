#!/usr/bin/env python
# -*- coding: utf-8 -*-


import _env
import re
import concurrent.futures
from io import open
from collections import namedtuple
from pprint import pprint
from requests.exceptions import ProxyError, ConnectTimeout

from lib._db import get_db
from html_parser import Bs4HtmlParser
from thread_pool_spider import ThreadPoolCrawler
from web_util import (
    get, logged, change_ip, get_proxy_dict, chunks, get_requests_proxy_ip

)


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
                value = getattr(self, func_name)(tag).strip()
            except Exception as e:
                print(e)
                value = ''
            yield self.pat.sub('', value)

    def parse(self):
        """parse

        :yields: many OrderedDict
        OrderedDict([('country', 'Cn'), ('ip', u'115.46.80.120'), ('port', u'8123'), ('address', u'\u5e7f\u897f\u5357\u5b81'), ('anonymous', u'\u9ad8\u533f'), ('type', u'HTTP'), ('speed', u'3.687\u79d2'), ('connect_time', u'0.737\u79d2'), ('live_time', u'1\u5206\u949f'), ('verify_time', u'16-07-26 10:54')])
        """
        table_tag = self.bs.find('table', id='ip_list')
        tr_tags = table_tag.find_all('tr')

        for tr_tag in tr_tags:
            td_tags = tr_tag.find_all('td')
            if td_tags:
                ip_info_tags = self.IpInfoTag(*td_tags)
                text_list = list(self.get_tags_text_from_tags(ip_info_tags))
                ip_info_texts = self.IpInfoText(*text_list)
                yield ip_info_texts._asdict()


@logged
class XiciCrawler(ThreadPoolCrawler):

    db = get_db('htmldb')
    col = getattr(db, 'xici_proxy')    # collection
    sleep = 10

    def init_urls(self):
        url = 'http://www.xicidaili.com/nn/%d'
        for i in range(1, 10):
            self.urls.append(url % i)

    def bulk_update_to_mongo(self, ip_dict_list):
        """bulk_update_to_mongo

        :param ip_dict_list:
        OrderedDict([('country', 'Cn'), ('ip', u'115.46.80.120'), ('port', u'8123'), ('address', u'\u5e7f\u897f\u5357\u5b81'), ('anonymous', u'\u9ad8\u533f'), ('type', u'HTTP'), ('speed', u'3.687\u79d2'), ('connect_time', u'0.737\u79d2'), ('live_time', u'1\u5206\u949f'), ('verify_time', u'16-07-26 10:54')])
        """
        bulk = self.col.initialize_ordered_bulk_op()
        for ip_info_dict in ip_dict_list:
            self.logger.info('%s', ip_info_dict['ip'])
            query_dict = {
                'ip': ip_info_dict['ip'],
                'port': ip_info_dict['port'],
            }
            update_dict = {
                '$set': ip_info_dict
            }
            bulk.find(query_dict).upsert().update(update_dict)

        bulk.execute()
        self.logger.info('count %d', self.col.count())

    def handle_response(self, url, response):
        """handle_response 把代理ip的信息存储到mongodb中

        :param url:
        :param response: requests.models.Response
        """
        self.logger.info('handle url: %s', url)
        if not response:
            return
        if response.status_code == 200:
            html = response.text
            html_parser = XiciHtmlParser(url, html)
            ip_info_dict_yield = html_parser.parse()
            self.bulk_update_to_mongo(ip_info_dict_yield)
        elif response.status_code == 503:
            change_ip()
            self.urls.append(url)    # retry


class KuaidailiHtmlParser(Bs4HtmlParser):
    fields = """ip, port, anonymous, type, address, speed, verify_time"""
    IpInfo = namedtuple('IpInfo', fields)

    def parse(self):
        table_tag = self.bs.find(
            'table', class_="table table-bordered table-striped"
        )
        tr_tags = table_tag.find_all('tr')
        for tr_tag in tr_tags[1:]:    # skip header
            td_tags = tr_tag.find_all('td')
            td_text_list = [tag.get_text().strip() for tag in td_tags]
            yield self.IpInfo(*td_text_list)._asdict()


@logged
class KuaidailiCrawler(ThreadPoolCrawler):

    """http://www.kuaidaili.com/"""
    db = get_db('htmldb')
    col = getattr(db, 'kuaidaili_proxy')    # collection
    sleep = 10

    def init_urls(self):
        _range = 1, 10
        for i in range(_range[0], _range[1] + 1):
            url = 'http://www.kuaidaili.com/free/inha/%d/' % i
            self.urls.append(url)

    def bulk_update_to_mongo(self, ip_dict_list):
        bulk = self.col.initialize_ordered_bulk_op()

        for ip_info_dict in ip_dict_list:
            self.logger.info('%s:%s', ip_info_dict['ip'], ip_info_dict['port'])
            query_dict = {
                'ip': ip_info_dict['ip'],
                'port': ip_info_dict['port'],
            }
            update_dict = {
                '$set': ip_info_dict
            }
            bulk.find(query_dict).upsert().update(update_dict)

        bulk.execute()
        self.logger.info('count %d', self.col.count())

    def handle_response(self, url, response):
        self.logger.info('handle url: %s', url)
        if not response:
            return
        if response.status_code == 200:
            html = response.text
            html_parser = KuaidailiHtmlParser(url, html)
            ip_info_dict_yield = html_parser.parse()
            self.bulk_update_to_mongo(ip_info_dict_yield)
        elif response.status_code == 503:
            change_ip()
            self.urls.append(url)    # retry


def get_proxy_from_kuaidaili(limit=10):
    """get_proxy_from_kuaidaili
    ":returns:" proxy dict requests can use directly
    """
    col = KuaidailiCrawler.col
    res = col.find().sort('speed').limit(limit)
    for doc in res:
        yield get_proxy_dict(doc['ip'], doc['port'])


def get_proxy_from_xici(limit=10):
    col = XiciCrawler.col
    res = col.find().sort('speed').limit(limit)
    for doc in res:
        yield get_proxy_dict(doc['ip'], doc['port'])


def test():
    url = 'http://www.xicidaili.com/nn'
    # html = get(url).text
    with open('./t.html', encoding='utf-8') as f:
        html = f.read()
        x = XiciHtmlParser(url, html)
        l = list(x.parse())
        for i in l:
            print(i)


def run_xici():
    xici_crawler = XiciCrawler()
    xici_crawler.run(use_thread=False)


def run_kuaidaili():
    c = KuaidailiCrawler()
    c.run(use_thread=False)

if __name__ == '__main__':
    # run_xici()
    check_proxy()
