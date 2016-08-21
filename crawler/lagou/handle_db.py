#!/usr/bin/env python
# -*- coding: utf-8 -*-

import _env
from pprint import pprint as pp
from tornado.util import ObjectDict
from lib._db import get_db, redis_client as r
from html_parser import Bs4HtmlParser
from lagou_parse import LagouHtmlParser
from spider import LagouCrawler
from web_util import logged


db = get_db('htmldb')
lagou_html_col = getattr(db, 'lagou_html')    # collection
lagou_job_col = getattr(db, 'lagou_job_col')


def test_get_db():
    o = col.find_one({'_id': 1234})
    html = o['html']
    # print html
    pp(o)


def test_get_html():
    import chardet
    _id = 46167
    o = col.find_one({'_id': _id})
    p = Bs4HtmlParser('', o['html'])
    print(p.html)
    t = p.bs.find('p', class_='msg')
    text = t.get_text()
    print(text)


def count_how_many_block_html():
    cnt = 0
    for html_doc in col.find(modifiers={"$snapshot": True}):
        html = html_doc['html']
        if LagouCrawler.is_block_html(html, False):
            cnt += 1
    return cnt


def count_how_many_check_html():
    print(col.count())
    cnt = 0
    _id_list = []
    for html_doc in col.find(modifiers={"$snapshot": True}):
        html = html_doc['html']
        if LagouCrawler.is_check_html(html, False):
            cnt += 1
            _id_list.append(html_doc._id)
    return cnt
    print(col.count())
    # col.remove({'_id':{'$in':_id_list}})


@logged
class ParseJob(object):
    """用来处理抓下来的html页面，把需要的数据从html中提取出来单独存储"""

    db = get_db('htmldb')

    def __init__(self):
        self.from_col = getattr(self.db, 'lagou_html')
        self.to_col = getattr(self.db, 'lagou_job')
        self.key = self.__class__.__name__
        self.last_id = int(r.get(self.key)) or 0

    def run_job(self):
        """lagou job页面的信息任务"""
        for doc_dict in self.col.find({'_id': {'$gte': self.last_id}}):
            if 'job' in doc_dict['url']:
                doc = ObjectDict(doc_dict)
                assert doc_dict.url and doc.html
                job_parser = LagouHtmlParser(doc.url, doc.html)
                data_dict = job_parser.parse_job()
                self.logger.info(
                    'handle url: %s %s:%s',
                    doc.url, data_dict['source'], data_dict['job_name']
                )
                self.to_col.update(
                    {
                        '_id': doc._id,
                    },
                    {
                        '$set': data_dict
                    },
                    upsert=True
                )


if __name__ == '__main__':
    # test_get_html()
    # print(count_how_many_block_html())
    # print(count_how_many_check_html())
    # print(col.count())
    p = ParseJob()
    p.run_job()
