#!/usr/bin/env python
# -*- coding:utf-8 -*-


from _db import redis_client as r


def gid(key="GID"):
    """generate and return grow id of key

    :param key: key string
    """
    return r.incr(key)


def reset_gid(key="GID"):
    r.set(key, 0)


if __name__ == '__main__':
    reset_gid()
    print(gid())
