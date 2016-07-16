#!/usr/bin/env python
# -*- coding:utf-8 -*-

import _env
from extract import *
import requests


def fetch_currency(url='http://fx.cmbchina.com/hq/'):
    html = requests.get(url, timeout=60).content.decode("utf-8","ignore")
    all_currency = extract_all('<td class="fontbold">', '</td>', html)
    return all_currency


def fetch_currency_page(name="美元",
                        url='http://fx.cmbchina.com/Hq/History.aspx?nbr=%s&page=1'):
    url = url % name
    html = requests.get(url, timeout=60).content.decode("utf-8","ignore")
    last_page = list(extract_all('<a href="', 'class="text"',
                    extract('<div class="function">', '<div', html)))[-1]
    last_page_num = int(extract('page=', '"', last_page))
    tr_list = extract_all('<tr>', '</tr>', html)
    for tr in tr_list:
        td_date = extract('<td align="center">', '</td>', tr)
        if td_date:
            td_middle_rate = list(extract_all('<td class="numberright">',
                                            '</td>',tr))[-1]
            print(td_date, td_middle_rate)

'''
for name in fetch_currency():
    url = 'http://fx.cmbchina.com/Hq/History.aspx?nbr=%s&page=36' % name
    print(requests.get(url).content)
    break
'''

fetch_currency_page()
