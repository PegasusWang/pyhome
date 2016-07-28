#!/usr/bin/env python
# -*- coding: utf-8 -*-


import _env
import re
import concurrent.futures
from io import open
from collections import namedtuple
from pprint import pprint

from lib._db import get_db
from html_parser import Bs4HtmlParser
from thread_pool_spider import ThreadPoolCrawler
from web_util import get, logged, change_ip, get_proxy_dict, chunks


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
    sleep = 3

    def init_urls(self):
        url = 'http://www.xicidaili.com/nn/%d'
        for i in range(1, 960):
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


@logged
class CheckXiciCralwer(ThreadPoolCrawler):
    """CheckXiciCralwer 用来测试代理的有效性，及时剔除没用的代理"""

    db = get_db('htmldb')
    col = getattr(db, 'xici_proxy')    # collection
    timeout = 20    # 测试超时时间

    def init_urls(self):
        """init_urls get all ip proxy from monggo"""
        url = 'http://www.baidu.com'
        for ip_info in self.col.find(no_cursor_timeout=True)[:100]:
            ip, port = ip_info['ip'], ip_info['port']
            if ip and port:
                self.urls.append((url, ip, port))    # tuple

    def run_async(self):
        for url_list in chunks(self.urls, 10):    # handle 100 every times
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
                    except Exception as e:
                        # import traceback
                        # traceback.print_exc()
                        print(e)
                    else:
                        self.handle_response(url, response)
            break    # TODO  remoe after test success

    def handle_response(self, url, response):
        """handle_response 验证代理的合法性。通过发送简单请求检测是否超时"""
        if response:
            self.logger.info('url: %s', url, response.status_code)


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


def check_proxy():
    c = CheckXiciCralwer()
    c.run()


if __name__ == '__main__':
    check_proxy()
