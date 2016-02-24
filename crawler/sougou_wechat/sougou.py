#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import logging
import random
import time
import traceback
import urllib.parse as urlparse
from urllib.parse import urlencode, quote
from iwgc import name_list
from ztz.db._mongo import QWECHAT
from ztz.util.extract import extract
from ztz.util.req import requests, parse_curl_str
from ztz.redis.gid import gid
from ztz.redis._redis import redis as _redis

"""搜狗微信爬虫，先根据公众号名字拿到列表页，如果第一个匹配就转到第一个搜索结果的页面, 再遍历每个公众号的文章列表页面。需要定期更新cookies。
"""


class DocumentExistsException(Exception):
    pass


def logged(class_):
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    class_.logger = logging.getLogger(class_.__name__)
    return class_


@logged
class SougouWechat:
    headers = None
    curl_str = """
    curl 'http://weixin.sogou.com/gzhjs?openid=oIWsFt2uCBiQ3mWa2BSUtmdKD3gs&ext=&cb=sogou.weixin_gzhcb&page=13&gzhArtKeyWord=&tsn=0&t=1455693188126&_=1455692977408' -H 'Cookie: SUV=00A27B2BB73D015554D9EC5137A6D159; ssuid=6215908745; SUID=2E0D8FDB66CA0D0A0000000055323CAB; usid=g6pDWznVhdOwAWDb; CXID=9621B02E3A96A6AB3F34DB9257660015; SMYUV=1448346711521049; _ga=GA1.2.1632917054.1453002662; ABTEST=8|1455514045|v1; weixinIndexVisited=1; ad=G7iNtZllll2QZQvQlllllVbxBJtlllllNsFMpkllllUlllllRTDll5@@@@@@@@@@; SNUID=C1B8F6463A3F10F2A42630AD3BA7E3E1; ppinf=5|1455520623|1456730223|Y2xpZW50aWQ6NDoyMDE3fGNydDoxMDoxNDU1NTIwNjIzfHJlZm5pY2s6NzpQZWdhc3VzfHRydXN0OjE6MXx1c2VyaWQ6NDQ6NENDQTE0NDVEMTg4OTRCMTY1MUEwMENDQUNEMEQxNThAcXEuc29odS5jb218dW5pcW5hbWU6NzpQZWdhc3VzfA; pprdig=Xmd5TMLPOARs3V2jIAZo-5UJDINIE0oFY97uU510_JOZm2-uu5TnST5KKW3oDgJY6-xd66wDhsb4Nm8wbOh1FCPohYO12b1kCrFoe-WUPrvg9JSqC72rjagjOlDg-JX72LcIjFOhsj7l_YGuaJpDrjFPoqy39C0AReCpmVcI5SM; PHPSESSID=e8vhf5d36raupjdb73k1rp7le5; SUIR=C1B8F6463A3F10F2A42630AD3BA7E3E1; sct=21; ppmdig=145569047300000087b07d5762b93c817f4868607c9ba98c; LSTMV=769%2C99; LCLKINT=47772; IPLOC=CN2200' -H 'Accept-Encoding: gzip, deflate, sdch' -H 'Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36' -H 'Accept: text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01' -H 'Referer: http://weixin.sogou.com/gzh?openid=oIWsFt2uCBiQ3mWa2BSUtmdKD3gs&amp;ext=lA5I5al3X8DLRO7Ypz8g44dD75TkiekfFoGEDMmpUgIjEtQirDGcaSXT-vwsAyxo' -H 'X-Requested-With: XMLHttpRequest' -H 'Connection: keep-alive' --compressed
    """

    def __init__(self, wechat_name, col_name='post'):
        self.col = getattr(QWECHAT, col_name)
        self.name = wechat_name    # 微信公众号名称
        self.key = '_'.join([self.__class__.__name__, self.name]).upper()
        if self.headers is None:
            self.update_headers()

    @property
    def page(self):
        _page = _redis.get(self.key)
        return int(_page) if _page else 1

    @page.setter
    def page(self, page):
        _redis.set(self.key, page)

    @staticmethod
    def getSUV():
        """模拟js代码生成suv"""
        return "SUV=" + quote(
            str(int(time.time()*1000)*1000 + round(random.random()*1000))
        )

    @classmethod
    def get_headers(cls):
        url, headers, data = parse_curl_str(cls.curl_str)
        del headers['Cookie']
        return headers

    @classmethod
    def get_cookie_str(cls):
        """生成一个搜狗微信的cookie并返回
        """
        while True:
            time.sleep(5)
            url = 'http://weixin.sogou.com/weixin?query=%s' % random.choice('abcdefghijklmnopqrstuvwxyz')

            # 获取SNUID
            cookie = requests.get(url, headers=cls.get_headers())
            headers = cookie.headers
            cookie_str = headers.get('Set-Cookie') + '; ' + SougouWechat.getSUV()
            # 跳过没有设置SNUID的
            if 'SUID' in cookie_str and 'SNUID' in cookie_str:
                return cookie_str

    @classmethod
    def update_headers(cls):
        cls.logger.info('*********updating cookies*********')
        _, headers, _ = parse_curl_str(cls.curl_str)
        headers['Cookie'] = cls.get_cookie_str()
        cls.headers = headers

    def search(self, retries=3):
        """搜索搜狗微信公众号并返回公众号文章列表页面,返回列表格式如下
        http://weixin.sogou.com/gzh?openid=oIWsFt2uCBiQ3mWa2BSUtmdKD3gs&amp;ext=p8lVKENENbkGdvuPNCqHoUqzuLEPtZheP6oyzp3YVsY_-OJEvXMz4yk2nJytyUxY
        """
        if self.page > 10:
            self.logger.info("抓取前10页结束: %s" % self.name)
            return None
        query_url = 'http://weixin.sogou.com/weixin?type=1&' + \
            urlencode({'query': self.name})
        self.logger.info(query_url)

        while retries > 0:
            self.logger.info('retry search %s %d' % (self.name, retries))
            html = requests.get(query_url, headers=self.headers).text
            href = extract('<div class="wx-rb bg-blue wx-rb_v1 _item" href="',
                           '"', html)
            if href:
                break
            else:
                self.update_headers()
                time.sleep(3)
            retries -= 1

        res = ('http://weixin.sogou.com' + href) if href else None
        return res

    def fetch_article_list(self, url, update=False):
        """ 微信号列表页面获取文章列表，返回json格式的数据，请求如下
        http://weixin.sogou.com/gzhjs?openid=oIWsFt0qY9YvyYESHey3MOPfbNy0&ext=lA5I5al3X8CtYOmsUDOgMhZWHWk6xQhEnWXQ_8nrROTPnk351KTH-rcTJUTGDdZq&cb=sogou.weixin_gzhcb&page=3
        """
        query_url = 'http://weixin.sogou.com/gzhjs?cb=sogou.weixin_gzhcb&'
        query_dict = dict(urlparse.parse_qsl(urlparse.urlsplit(url).query))

        while True:
            page = self.page
            if update and page > 2:
                page = 1
            if not update and page > 10:
                break
            self.logger.info('抓取:%s page: %d' % (self.name, page))
            query_dict['page'] = page
            json_url = query_url + urlencode(query_dict)
            json_str = requests.get(json_url, headers=self.headers).text
            try:
                url_list, total_pages = self.parse_list_page(json_str.strip())
            except Exception:
                traceback.print_exc()
                self.update_headers()
                continue

            if not url_list or page > min(10, total_pages):    # 非登录只能抓100条
                self.logger.info('%s爬取完毕' % self.name)
                break

            try:
                for page_url in url_list:
                    time.sleep(1.5)     # sougou频率限制
                    self.logger.info(page_url)
                    self.fetch_ori_page(page_url)
            except DocumentExistsException:
                self.logger.info("更新完毕")
                break
            except Exception:
                traceback.print_exc()
                self.update_headers()
                continue

            page += 1
            self.page = page

    def parse_list_page(self, json_str):
        """解析文章列表json数据，返回文章url列表和页数"""
        try:
            json_str = json_str[json_str.find('(')+1: json_str.rfind(')')]
            o = json.loads(json_str)
            items = o.get('items')
            total_pages = int(o.get('totalPages'))
            url_list = []
            for xml_str in items:
                url_list.append(
                    extract('<url><![CDATA[', ']]></url>', xml_str)
                )
            _url = 'http://weixin.sogou.com'
            return [_url+url for url in url_list], total_pages
        except Exception:
            time.sleep(10)
            raise Exception("retry")

    def fetch_ori_page(self, page_url):
        """拿到单个文章页面，在文章url里加上参数f=json可以直接得到json格式的数据"""
        # 先拿到搜狗跳转到微信文章的地址
        pre_r = requests.get(page_url, headers=self.headers)
        wechat_url = pre_r.url.split('#')[0] + '&f=json'

        if 'mp.weixin' not in wechat_url:
            return

        r = requests.get(wechat_url, headers=self.headers)
        self.logger.info(wechat_url)
        if self.col.find_one(nick_name=self.name, url=wechat_url):
            raise DocumentExistsException("article exist")
        if r.status_code != 200:
            return

        o = json.loads(r.text)
        self.col.upsert(_id=gid(), nick_name=self.name, url=wechat_url)(json=o)

    def fetch_page(self, page_url):
        """拿到单个文章页面，在文章url里加上参数f=json可以直接得到json格式的数据"""
        # 先拿到搜狗跳转到微信文章的地址
        pre_r = requests.get(page_url, headers=self.headers)
        wechat_url = pre_r.url.split('#')[0] + '&f=json'

        if 'mp.weixin' not in wechat_url:
            return

        r = requests.get(wechat_url, headers=self.headers)
        self.logger.info(wechat_url)
        if self.col.find_one(nick_name=self.name, url=wechat_url):
            raise DocumentExistsException("article exist")
        if r.status_code != 200:
            return

        o = json.loads(r.text)
        fields = {'cdn_url', 'nick_name', 'title', 'content',
                  'link', 'ori_create_time'}
        article_dict = {k: o.get(k) for k in fields}
        if self.col.find_one(nick_name=self.name, title=o['title']):
            raise DocumentExistsException("article exist")
        if o['title'] and o['content']:
            article_dict['nick_name'] = self.name
            article_dict['url'] = wechat_url
            self.col.upsert(_id=gid())(**article_dict)

    def fetch(self, update=False):
        url = self.search()
        if url:
            self.fetch_article_list(url, update)
        else:
            self.logger.info('抓取结束或找不到微信号 %s\n' % self.name)
        self.logger.info('抓取结束 %s\n' % self.name)

    def update(self):
        self.fetch(update=True)


def fetch_all(_id=1, update=False):
    name_li = name_list(_id=_id)
    name_li.sort()
    for index, name in enumerate(name_li):
        s = SougouWechat(name)
        if update:
            s.update()
        else:
            s.fetch()
        print('剩余%d个微信号待抓取' % (len(name_li)-index-1))


if __name__ == '__main__':
    fetch_all(7)
    fetch_all(1)
