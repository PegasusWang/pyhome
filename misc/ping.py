#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""ping脚本，有新文章发布的时候通知搜索引擎.
只需要标注库, 支持python3
"""


import os
import re
import time
try:
    from urllib2 import urlopen
    from xmlrpclib import ServerProxy
except ImportError:    # py3
    from urllib.request import urlopen
    from xmlrpc.client import ServerProxy


def ping(ping_url, site_name, site_host, post_url, rss_url):
    """ping single service"""
    print('ping...', ping_url, post_url)
    rpc_server = ServerProxy(ping_url)
    result = rpc_server.weblogUpdates.extendedPing(
        site_name, site_host, "http://"+post_url, "http://"+rss_url
    )
    print(result)    # baidu return 0 means ping success
    with open('./ping.txt', 'a+') as f:    # save url
        f.write(post_url+'\n')


def ping_all(site_name, site_host, post_url, rss_url):
    ping_url_list = [
        'http://ping.baidu.com/ping/RPC2', # http://zhanzhang.baidu.com/tools/ping
        #'http://rpc.pingomatic.com/',    # must every 5 minutes
        #'http://blogsearch.google.com/ping/RPC2',
        #'http://api.my.yahoo.com/RPC2',
        #'http://blog.youdao.com/ping/RPC2',
        #'http://ping.feedburner.com',
    ]
    for ping_url in ping_url_list:
        try:
            ping(ping_url, site_name, site_host, post_url, rss_url)
        except Exception as e:
            print('ping fail', post_url, e)
            continue


def get_all_post_url(rss_url='http://jishushare.com/sitemap-posts.xml'):
    """rss_url 博客的rss地址, 用来拿到所有文章"""
    response = urlopen(rss_url)
    html = response.read().decode('utf-8')    # your sitemap page encoding
    pat = re.compile('<loc>http://(.*?)</loc>')
    url_list = ['http://'+url.strip() for url in pat.findall(html)]
    return set(url_list)


def get_already_ping_url(f='./ping.txt'):
    """防止重复ping，在ping.txt里保存已经ping过的url"""
    if not os.path.exists(f):
        open(f, 'a').close()
    with open(f, 'r') as f:
        return set([url.strip() for url in f.readlines() if url])


def test():
    site_name = "技术分享网"
    site_host = "http://jishushare.com/"
    post_url = 'http://jishushare.com/duo-xian-cheng-yi-bu-yi-bu-duo-jin-cheng-pa-chong/'
    rss_url = "http://jishushare.com/sitemap-posts.xml"
    ping_all(site_name, site_host, post_url, rss_url)


def ping_jishushare():
    to_ping_url_list = get_all_post_url() - get_already_ping_url()
    site_name = "技术分享网"
    site_host = "http://jishushare.com/"
    rss_url = "http://jishushare.com/sitemap-posts.xml"
    for post_url in to_ping_url_list:
        time.sleep(10)
        ping_all(site_name, site_host, post_url, rss_url)


def ping_ningningtoday():
    rss_url = 'http://ningning.today/sitemap.xml'
    to_ping_url_list = get_all_post_url(rss_url) - get_already_ping_url()
    site_name = "Pegasus的博客"
    site_host = "http://ningning.today/"
    for post_url in to_ping_url_list:
        time.sleep(10)
        ping_all(site_name, site_host, post_url, rss_url)


def ping_pythome():
    rss_url = "http://pyhome.org/sitemap-posts.xml"
    to_ping_url_list = get_all_post_url(rss_url) - get_already_ping_url()
    site_name = "Python之家"
    site_host = "http://pyhome.org/"
    for post_url in to_ping_url_list:
        time.sleep(5)
        ping_all(site_name, site_host, post_url, rss_url)


if __name__ == '__main__':
    ping_pythome()
    print('finish')
