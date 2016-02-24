#!/usr/bin/env python
# -*- coding:utf-8 -*-

import _env
from lib._db import get_collection
from extract import extract, extract_all
from web_util import requests
from config.config import CONFIG

"""
抓取http://www.iwgc.cn/网站微信公众号列表
<a href="/1" id="cat-1" class="list-group-item">创意&middot;科技</a>
<a href="/2" id="cat-2" class="list-group-item">媒体&middot;达人</a>
<a href="/3" id="cat-3" class="list-group-item">摄影&middot;旅行</a>
<a href="/4" id="cat-4" class="list-group-item">生活&middot;家居</a>
<a href="/5" id="cat-5" class="list-group-item">学习&middot;工具</a>
<a href="/6" id="cat-6" class="list-group-item">历史&middot;读书</a>
<a href="/7" id="cat-7" class="list-group-item">金融&middot;理财</a>
<a href="/8" id="cat-8" class="list-group-item">电影&middot;音乐</a>
<a href="/9" id="cat-9" class="list-group-item">美食&middot;菜谱</a>
<a href="/10" id="cat-10" class="list-group-item">外语&middot;教育</a>
<a href="/11" id="cat-11" class="list-group-item">宠物&middot;休闲</a>
<a href="/12" id="cat-12" class="list-group-item">健康&middot;医疗</a>
<a href="/13" id="cat-13" class="list-group-item">时尚&middot;购物</a>
<a href="/14" id="cat-14" class="list-group-item">公司&middot;宣传</a>
<a href="/15" id="cat-15" class="list-group-item">游戏&middot;娱乐</a>

"""

COL = get_collection(CONFIG.MONGO.DATABASE, 'wechat_name')


def wechat_list():
    for _id in range(1, 16):
        url = 'http://www.iwgc.cn/%d' % _id
        page = 1
        res = []

        while True:
            page_url = url + '/p/' + str(page)
            html = requests.get(page_url).text
            detail_list = extract_all('<div class="detail">', '</div>', html)
            name_list = [extract('title="', '"', tag) for tag in detail_list]
            if not name_list:
                break
            else:
                res.extend(name_list)
            page += 1

        COL.update(
            {'_id': _id},
            {
                '$set': {'name_list': res}
            },
            upsert=True
        )


def name_list(_id):
    l = COL.find_one(_id).get('name_list')
    return [s.strip() for s in set(l)]


if __name__ == '__main__':
    wechat_list()
    for i in name_list(1):
        print(i)
