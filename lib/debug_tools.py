#!/usr/bin/env python
# -*- coding:utf-8 -*-

from collections import Iterable


def flatten(items, ignore_types=(str, bytes)):
    for x in items:
        if isinstance(x, Iterable) and not isinstance(x, ignore_types):
            for i in flatten(x):
                yield i
            # yield from flatten(x)    # py3
    else:
        yield x


def print_li(li):
    if isinstance(li, (list, tuple)):
        for i in li:
            print_li(i)
    elif isinstance(li, (str, unicode)):
        print(li)
    elif isinstance(li, dict):
        for k, v in li.items():
            print(k, v)
    else:
        print(li)
