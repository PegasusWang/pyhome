#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lib._db import redis_client as r


class IncrId(object):
    def __init__(self, key):
        self.key = '_'.join([key, self.__class__.__name__])

    def get(self):
        return int(r.incr(self.key))

    def reset(self):
        r.set(self.key, 0)


class UrlManager(object):
    def __init__(self, domain):
        """__init__ use zset to store url.
        :param domain: domain as redis set key
        """
        self.domain_zset = domain    # zset key
        self.incr_id = IncrId(domain)
        # 每次zset中删除一个url就在set中增加一个url，方面统计有多少已经抓了
        self.remain_set = self.domain_zset + '_rem'

    def add_url(self, url):
        """add_url

        :param url: single or url list
        """
        if isinstance(url, (list, tuple)):
            self.add_url_list(url)
        else:
            r.zadd(self.domain_zset, self.incr_id.get(), url)

    def add_url_list(self, url_list, chunks=1000):
        for chunk_url_list in self.chunks(url_list, chunks):
            p = r.pipeline()
            for url in chunk_url_list:
                p.zadd(self.domain_zset, self.incr_id.get(), url)
            p.execute()

    def remove_url(self, url):
        r.sadd(self.remain_set, url)
        return r.zrem(self.domain_zset, url)

    def url_nums_has_crawler(self):
        return r.scard(self.remain_set)

    @staticmethod
    def chunks(l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i+n]

    def url_nums(self):
        return r.zcard(self.domain_zset)

    def has_url(self, url):
        return bool(r.zscore(self.domain_zset, url))

    def first_url(self):
        rl = r.zrange(self.domain_zset, 0, 0)    # min score
        return rl[0] if rl else None

    def last_url(self):
        rl = r.zrange(self.domain_zset, -1, -1)    # max score
        return rl[0] if rl else None

    def delay_url(self, url, nums):
        """delay_url 给当前url增加score使得改url延后抓取

        :param url: url as redis zset key
        :param nums: 推迟多少个url以后抓取
        :return: new int score
        """
        return int(r.zincrby(self.domain_zset, nums, url))
