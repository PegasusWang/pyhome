#!/usr/bin/env python
# -*- coding:utf-8 -*-

import requests
from lxml import etree


def get_proxies_from_site():
    url = 'http://proxy.ipcn.org/country/'
    xpath = '/html/body/div[last()]/table[last()]/tr/td/text()'

    r = requests.get(url)
    tree = etree.HTML(r.text)

    results = tree.xpath(xpath)
    proxies = [line.strip() for line in results]

    return proxies

#使用http://lwons.com/wx网页来测试代理主机是否可用
def get_valid_proxies(proxies, count):
    url = 'http://lwons.com/wx'
    results = []
    cur = 0
    for p in proxies:
        proxy = {'http': 'http://' + p}
        succeed = False
        try:
            r = requests.get(url, proxies=proxy)
            if r.text == 'default':
                succeed = True
        except Exception, e:
            print 'error:', p
            succeed = False
        if succeed:
            print 'succeed:', p
            results.append(p)
            cur += 1
            if cur >= count:
                break

if __name__ == '__main__':
    print 'get ' + str(len(get_valid_proxies(get_proxies_from_site(), 20))) + ' proxies'

