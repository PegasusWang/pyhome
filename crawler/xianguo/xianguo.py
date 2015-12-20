#!/usr/bin/env python
# -*- coding:utf-8 -*-


import _env
import json
import requests
from pprint import pprint
from lib._db import get_collection
from config.config import CONFIG
DB = CONFIG.MONGO.DATABASE

try:
    from Queue import Queue
except ImportError:
    from queue import Queue

URL = 'http://api.xianguo.com/i/status/get.json?key=36d979af3f6cecd87b89720d3284d420'


def to_dict(form):
    d = {}
    arg_list = form.rstrip('&').split('&')
    for i in arg_list:
        k = i.split('=')[0]
        v = i.split('=')[1]
        d[k] = v
    return d


def fetch(url, data_dict=None):
    return requests.post(url, data=data_dict, timeout=10).text


def xianguo_spider(q, coll_name='tech', max_news_num=1000):
    _COLL = get_collection(DB, coll_name)
    while True:
        while not q.empty():
            url, data_dict = q.get()
            try:
                html = fetch(url, data_dict)
            except Exception as e:
                print(e)
                continue

            if not html or html == 'null':    # xianguo may returns null
                return

            o = json.loads(html)
            to_save = ['source', 'content',
                       'url', 'title', 'time', 'brief']
            id_list = []

            for i in o:
                d = {}
                docid = i.get('id')
                id_list.append(docid)
                section_id = i.get('user').get('id')
                source = i.get('user').get('username')
                content = i.get('linkcontent').get('content')
                url = i.get('linkcontent').get('originalurl')
                title = i.get('linkcontent').get('title')
                time = i.get('time')
                if time is None or time == 'None':
                    time = 0

                brief = i.get('content')
                for k, v in list(locals().items()):
                    if k in to_save:
                        d[k] = v

                _COLL.update(
                    {'_id': int(docid)},
                    {
                        '$set': d
                    },
                    True
                )
            maxid = min(id_list)

            form_dict = dict(
                devicemodel='motorola-XT1079',
                isShowContent=1,
                maxid=int(maxid),
                sectionid=int(section_id),
                sectiontype=0,
                version=77,
                count=25,
                udid=355456060447393,
                devicetype=5,
                isThumb=0
            )
            print('new url', form_dict.get('maxid'), form_dict.get('sectionid'))

            for i in id_list:
                if _COLL.find_one({'_id': int(i)}):
                    print('************Finish#############')
                    return

            q.put((URL, form_dict))    # put a tuple


PYTHON_ID = """python.cn(jobs, news) 1766610
Python文档 1017851
Planet Python 1017844
豆瓣Python编程小组 1017845
learning python 1017849
老王python 1762185"""


def get_sectionid_list(title_section_str):
    name_list = (title_section_str.split('\n'))
    res = []
    for i in name_list:
        l = i.split()
        res.append(l[len(l)-1])
    return res


def run_spider(title_section_str, coll_name):
    q = Queue()
    formstr = 'devicemodel=motorola-XT1079&isShowContent=1&maxid=1000000000&sectionid=%d&sectiontype=0&version=77&count=25&udid=355456060447393&devicetype=5&isThumb=1&'
    for sid in get_sectionid_list(title_section_str):
        s = formstr % (int(sid))
        print(s)
        q.put((URL, to_dict(s)))
        xianguo_spider(q, coll_name)


def main():
    for s in ['PYTHON']:
        title_section_str = globals().get(s+'_ID')
        coll_name = s.lower()
        run_spider(title_section_str, coll_name)


if __name__ == '__main__':
    main()
