#!/usr/bin/env python
# -*- coding: utf-8 -*-

import _env
from extract import extract
from tornado import gen
from async_spider import AsySpider
from lib._db import get_collection
from jb51_parse import parse_jb51
from config.config import CONFIG
DB = CONFIG.MONGO.DATABASE


def is_python_article(data_dict):
    title = data_dict.get('title').lower()
    content = data_dict.get('content').lower()
    if ('python' in title) or ('python' in content):
        return True
    return False


class Jb51Spider(AsySpider):
    def __init__(self, urls, concurrency=10, results=None, **kwargs):
        super(Jb51Spider, self).__init__(urls, concurrency, results, **kwargs)
        self.db = get_collection(DB, 'article_pyhome', 'motor')    # change coll

    @gen.coroutine
    def update_doc(self, url, data_dict):
        yield self.db.update(
            {'source_url': url},
            {
                '$set': data_dict
            },
            True
        )

    @gen.coroutine
    def handle_html(self, url, html):
        print(url)
        data = parse_jb51(html)
        if is_python_article(data):
            print('is python article')
            data['source_url'] = url
            data['read_count'] = 0
            data['source'] = 'www.jb51.net'
            yield self.update_doc(url, data)


if __name__ == '__main__':
    import sys
    try:
        beg, end = int(sys.argv[1]), int(sys.argv[2])
    except:
        beg, end = 10, 20
    urls = []
    for page in range(beg, end):
        urls.append('http://www.jb51.net/article/%s.htm' % page)
    s = Jb51Spider(urls)
    s.run()
