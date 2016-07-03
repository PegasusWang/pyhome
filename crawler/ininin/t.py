#!/usr/bin/env python
# -*- coding:utf-8 -*-

import _env
import json
import logging
import random
import sys
import time
import traceback

import six.moves.urllib.parse as urlparse   # for py2 and py3 use six
from six.moves.urllib.parse import urlencode, quote
from bs4 import BeautifulSoup
from single_process import single_process

from config.config import CONFIG
from extract import extract
from iwgc import name_list, tagid_by_name
from lib._db import get_mongodb
from lib._db import redis_client as _redis
from lib.redis_tools import gid
from lib.date_util import datestr_from_stamp, days_from_now
from web_util import get, parse_curl_str, change_ip

"""搜狗微信爬虫，先根据公众号名字拿到列表页，如果第一个匹配就转到第一个搜索结果
的页面, 再遍历每个公众号的文章列表页面。需要定期更新cookies。
"""


class DocumentExistsException(Exception):
    pass


class DocumentExpireException(Exception):
    """用来控制超过一定天数后就跳过"""
    pass


def logged(class_):
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    class_.logger = logging.getLogger(class_.__name__)
    return class_


@logged
class SougouWechat:
    db = get_mongodb(CONFIG.MONGO.DATABASE, client='mongo')
    headers = None
    curl_str = """
    curl 'http://weixin.sogou.com/gzhjs?openid=oIWsFt2uCBiQ3mWa2BSUtmdKD3gs&ext=&cb=sogou.weixin_gzhcb&page=13&gzhArtKeyWord=&tsn=0&t=1455693188126&_=1455692977408' -H 'Cookie: SUV=00A27B2BB73D015554D9EC5137A6D159; ssuid=6215908745; SUID=2E0D8FDB66CA0D0A0000000055323CAB; usid=g6pDWznVhdOwAWDb; CXID=9621B02E3A96A6AB3F34DB9257660015; SMYUV=1448346711521049; _ga=GA1.2.1632917054.1453002662; ABTEST=8|1455514045|v1; weixinIndexVisited=1; ad=G7iNtZllll2QZQvQlllllVbxBJtlllllNsFMpkllllUlllllRTDll5@@@@@@@@@@; SNUID=C1B8F6463A3F10F2A42630AD3BA7E3E1; ppinf=5|1455520623|1456730223|Y2xpZW50aWQ6NDoyMDE3fGNydDoxMDoxNDU1NTIwNjIzfHJlZm5pY2s6NzpQZWdhc3VzfHRydXN0OjE6MXx1c2VyaWQ6NDQ6NENDQTE0NDVEMTg4OTRCMTY1MUEwMENDQUNEMEQxNThAcXEuc29odS5jb218dW5pcW5hbWU6NzpQZWdhc3VzfA; pprdig=Xmd5TMLPOARs3V2jIAZo-5UJDINIE0oFY97uU510_JOZm2-uu5TnST5KKW3oDgJY6-xd66wDhsb4Nm8wbOh1FCPohYO12b1kCrFoe-WUPrvg9JSqC72rjagjOlDg-JX72LcIjFOhsj7l_YGuaJpDrjFPoqy39C0AReCpmVcI5SM; PHPSESSID=e8vhf5d36raupjdb73k1rp7le5; SUIR=C1B8F6463A3F10F2A42630AD3BA7E3E1; sct=21; ppmdig=145569047300000087b07d5762b93c817f4868607c9ba98c; LSTMV=769%2C99; LCLKINT=47772; IPLOC=CN2200' -H 'Accept-Encoding: gzip, deflate, sdch' -H 'Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36' -H 'Accept: text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01' -H 'Referer: http://weixin.sogou.com/gzh?openid=oIWsFt2uCBiQ3mWa2BSUtmdKD3gs&amp;ext=lA5I5al3X8DLRO7Ypz8g44dD75TkiekfFoGEDMmpUgIjEtQirDGcaSXT-vwsAyxo' -H 'X-Requested-With: XMLHttpRequest' -H 'Connection: keep-alive' --compressed
    """

    def __init__(self, wechat_name, tag_id, limit=CONFIG.CRAWLER.LIMIT,
                 col_name='wechat_post',
                 media_col_name="wechat_media"):
        self.col = getattr(self.db, col_name)
        self.media_col = getattr(self.db, media_col_name)
        self.name = wechat_name    # 微信公众号名称
        self.tag_id = tag_id
        self.limit = limit
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
            url = 'http://weixin.sogou.com/weixin?query=%s' % \
                random.choice('abcdefghijklmnopqrstuvwxyz')

            # 获取SNUID
            cookie = get(url, headers=cls.get_headers())
            headers = cookie.headers
            try:
                cookie_str = headers.get('Set-Cookie') + '; ' + \
                    SougouWechat.getSUV()
            except Exception:
                cookie_str = None

            cls.logger.info('cookie_str: %s' % cookie_str)
            # 跳过没有设置SNUID的
            if cookie_str and 'SUID' in cookie_str and 'SNUID' in cookie_str:
                return cookie_str

    @classmethod
    def update_headers(cls):
        cls.logger.info('*********updating cookies*********')
        _, headers, _ = parse_curl_str(cls.curl_str)
        headers['Cookie'] = cls.get_cookie_str()
        if headers['Cookie'] is None:
            change_ip()
            cls.update_headers()
        else:
            cls.headers = headers

    def search(self, retries=3):
        """搜索搜狗微信公众号并返回公众号文章列表页面,返回列表格式如下
        http://weixin.sogou.com/gzh?openid=oIWsFt2uCBiQ3mWa2BSUtmdKD3gs&amp;ext=p8lVKENENbkGdvuPNCqHoUqzuLEPtZheP6oyzp3YVsY_-OJEvXMz4yk2nJytyUxY
        """
        if not self.name:
            return
        if self.page > 10:
            self.logger.info("抓取前10页结束: %s" % self.name)
            return None
        query_url = 'http://weixin.sogou.com/weixin?type=1&' + \
            urlencode({'query': self.name})
        self.logger.info(query_url)

        while retries > 0:
            self.logger.info('retry search %s %d' % (self.name, retries))
            html = get(query_url, headers=self.headers).text
            soup = BeautifulSoup(html)
            item_tag_li = soup.find_all('div',
                                        class_="wx-rb bg-blue wx-rb_v1 _item")
            href = None
            try:
                for item_tag in item_tag_li:
                    _href = item_tag.get('href')
                    _title = item_tag.find(class_='txt-box').h3.text
                    if _title.strip() == self.name.strip():
                        href = _href
                        break
            except Exception:
                self.logger.info('found %s failed' % self.name)
                continue

            if href is not None:
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
            json_str = get(json_url, headers=self.headers).text
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
                    time.sleep(random.randint(3, 10))     # sougou频率限制
                    self.logger.info(page_url)
                    self.fetch_page(page_url)
                    # self.fetch_ori_page(page_url)
            except (DocumentExistsException, DocumentExpireException):
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
        """拿到单个文章页面，在文章url里加上参数f=json可以直接得到
        json格式的数据。
        """
        # 先拿到搜狗跳转到微信文章的地址
        pre_r = get(page_url, headers=self.headers)
        wechat_url = pre_r.url.split('#')[0] + '&f=json'

        if 'mp.weixin' not in wechat_url:
            return

        r = get(wechat_url, headers=self.headers)
        self.logger.info(wechat_url)
        if self.col.find_one(dict(nick_name=self.name, url=wechat_url)):
            raise DocumentExistsException("article exist")
        if r.status_code != 200:
            return

        o = json.loads(r.text)
        self.col.update(
            {
                '_id': gid(),
                'nick_name': self.name,
                'url': wechat_url,
            },
            {
                '$set': {'json': o}
            },
            upsert=True
        )

    def fetch_page(self, page_url):
        """拿到单个文章页面，在文章url里加上参数f=json可以直接得到json格式
        的数据，处理json拿到需要的字段。
        """
        if self.col.find(dict(nick_name=self.name)).count() > self.limit:
            oldest_doc = list(self.col.find(dict(nick_name=self.name)).
                              sort([('ori_create_time', 1)]).limit(1))[0]
            oldest_doc_id = oldest_doc.get('_id')
            self.col.remove({'_id': oldest_doc_id})
            self.logger.info(
                "%s:删除:%s : %s\n" %
                (
                    self.name,
                    oldest_doc.get('title'),
                    datestr_from_stamp(
                        oldest_doc.get('ori_create_time'), '%Y-%m-%d'
                    )
                )
            )

        # 先拿到搜狗跳转到微信文章的地址
        pre_r = get(page_url, headers=self.headers)
        wechat_url = pre_r.url.split('#')[0] + '&f=json'

        if 'mp.weixin' not in wechat_url:
            return

        r = get(wechat_url, headers=self.headers)
        self.logger.info(wechat_url)
        if self.col.find_one(dict(nick_name=self.name, url=wechat_url)):
            raise DocumentExistsException("article exist")

        if r.status_code != 200:
            return

        o = json.loads(r.text)
        if o.get('title') is None:    # 文章被投诉后没有此字段，跳过
            return

        fields = {'cdn_url', 'nick_name', 'title', 'content', 'desc',
                  'link', 'ori_create_time'}
        media_fields = {'round_head_img', 'nick_name', 'signature'}
        media_dict = {k: o.get(k) for k in media_fields}
        article_dict = {k: o.get(k) for k in fields}

        if self.col.find_one(dict(nick_name=self.name, title=o['title'])):
            raise DocumentExistsException("article exist")

        too_old_days = 10
        if days_from_now(o['ori_create_time']) > too_old_days:    # 10天之前的跳过
            self.logger.info(
                '%s跳过%d天前文章 title : %s\n', self.name, too_old_days, o['title']
            )
            raise DocumentExpireException("expire")

        if o['title'] and o['content']:
            o_date = datestr_from_stamp(o.get('ori_create_time'), '%Y-%m-%d')
            self.logger.info(
                '%s-保存文章 title : %s %s\n', self.name, o['title'], o_date
            )

            article_dict['nick_name'] = self.name
            article_dict['url'] = wechat_url
            article_dict['tag_id'] = self.tag_id
            del article_dict['content']
            self.col.update(
                {
                    '_id': gid()
                },
                {
                    '$set': article_dict
                },
                True
            )

        # http://mp.weixin.qq.com/s?__biz=MjM5NjAxMDc4MA==&mid=404900944&idx=1&sn=fe2d53ce562ee51e7163a60d4c95484a#rd
        biz = extract('__biz=', '==', article_dict['link'])
        self.media_col.update(
            {'_id': biz},
            {
                '$set': media_dict
            },
            True
        )

    def fetch(self, update=False):
        url = self.search()
        if url:
            self.fetch_article_list(url, update)
        else:
            self.logger.info('抓取结束或找不到微信号 %s\n' % self.name)
        self.logger.info('抓取结束 %s\n' % self.name)

    def update(self):
        self.fetch(update=True)


def fetch(name):
    if name:
        tagid = tagid_by_name(name.strip())
        if tagid:
            print("tag_id: %d" % tagid)
            s = SougouWechat(name, tag_id=tagid, limit=CONFIG.CRAWLER.LIMIT)
            s.fetch()


def fetch_all(_id=1, li_name="name_list", update=False):
    name_li = name_list(_id, li_name)
    name_li.sort()
    for index, name in enumerate(name_li):
        s = SougouWechat(name, tag_id=_id, limit=CONFIG.CRAWLER.LIMIT)
        if update:
            s.update()
        else:
            s.fetch()
        print('剩余%d个微信号待抓取' % (len(name_li)-index-1))


@single_process
def main():
    try:
        name = sys.argv[1]
    except IndexError:
        to_fetch_id = list(range(16, 22))
        random.shuffle(to_fetch_id)
        for _id in to_fetch_id:
            fetch_all(_id, 'need_name_list')
        return

    fetch(name)

if __name__ == '__main__':
    main()

