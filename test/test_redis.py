#!/usr/bin/env python
# -*- coding: utf-8 -*-


from redis import StrictRedis
r = StrictRedis(host='127.0.0.1', port=6379)


def test():
    key = 'testkey'
    r.zadd(key, 0, 0)
    r.zadd(key, 1, '1')
    r.zadd(key, 2, '2')
    r.zadd(key, 3, '3')
    print(r.zrange(key, -1, -1))[0]
    print(type(r.zrange(key, -1, -1)[0]))

    print(r.zrange(key, 0, 0))[0]
    print(type(r.zrange(key, 0, 0)[0]))

    print(r.zcard(key))
    print(type(r.zcard(key)))


if __name__ == '__main__':
    test()
