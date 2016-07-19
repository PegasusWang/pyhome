#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lib._db import redis_cliet as r


class UrlManager(object):
    def __init__(self, domain):
        """__init__
        :param domain: domain as redis set key
        """
        self.domain = domain

    def add_url(self, url):
        """add_url

        :param url: single or url list
        """
        if isinstance(url, (list, tuple)):
            self.add_url_list(url)
        return r.add(self.domain, url)

    def add_url_list(self, url_list, chunks=1000):
        for chunk_url_list in self.chunks(url_list, chunks):
            p = r.pipeline()
            for url in chunk_url_list:
                p.add(self.domain, url)
            p.execute()

    def remove_url(self, url):
        return r.srem(self.domain, url)

    @staticmethod
    def chunks(l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i+n]

    def url_nums(self):
        return r.scard(self.domain)

    def has_url(self, url):
        return r.sismember(self.domain, url)
