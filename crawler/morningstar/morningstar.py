#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""晨星基金评级数据，用来买基金作为参考"""

import _env
import copy
import heapq
import requests
from operator import itemgetter
from tornado.escape import utf8
from six import print_
from bs4 import BeautifulSoup
from web_util import get


def parse_html(html):
    html = utf8(html)
    soup = BeautifulSoup(html)
    tb = soup.find('table', class_="fr_tablecontent")
    tr_li = tb.find_all('tr')
    for tr in tr_li:
        td_li = tr.find_all('td')
        for td in td_li:
            cxt = ''.join(td.get_text().split())    # remove space
            print_(cxt, end=' ')
        print_('\n')


def parse_txt(filepath):
    with open(filepath) as f:
        lines = f.readlines()
        for line in lines:
            d = line.strip().split()
            if d:
                assert len(d) == 14
                print_(d[0], end='\n')


def main():
    with open('./stock_fund.html') as f:
        parse_html(f.read())
    #parse_txt('./txt')


def fetch_parse():
    url = 'http://cn.morningstar.com/handler/fundranking.ashx?date=2016-04-08&fund=&category=mix_radical&rating=&company=&cust=&sort=Return2Year&direction=desc&tabindex=1&pageindex=1&pagesize=10000&randomid=0.043611296370827723'
    html = get(url).text
    parse_html(html)


def choose(filepath_txt, sort_index_list=[10, 8, 7]):
    """
    0   序号
    1   基金代码
    2   基金名称
    3   今年以来
    4   一周
    5   一个月
    6   三个月
    7   六个月
    8   一年
    9   两年
    10  三年
    11  五年
    12  十年
    13  设立以来
    """
    with open(filepath_txt, 'r') as f:
        lines = f.readlines()
        fund_array = []    # 2 demonsional array of fund_info
        for line in lines:
            info_list = line.strip().split()
            if info_list:
                for index, value in enumerate(info_list):
                    if index >= 3:
                        try:
                            value = float(value)
                        except ValueError:
                            value = 0.0
                        info_list[index] = value
                fund_array.append(info_list)

        num = 100
        for sort_index in sort_index_list:
            fund_array.sort(key=itemgetter(sort_index), reverse=True)
            fund_array = fund_array[0:num]
            num /= 2

        fund_str_array = [' '.join([str(i) for i in l]) for l in fund_array]
        res = '\n'.join(fund_str_array)
        with open('res', 'w') as f:
            f.write(res)


if __name__ == '__main__':
    choose('./log')
