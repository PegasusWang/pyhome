#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
some functions extract html tag,
more faster than bs4
使用之前最好用
html = "".join(s.split())
去除所有换行符、空格、tag等
"""


import re

def extract(begin, end, html):
    if not html:
        return ''
    start = html.find(begin)
    if start >= 0:
        start += len(begin)
        if end is not None:
            end = html.find(end, start)
        if end is None or end >= 0:
            return html[start:end].strip()


def extract_all(begin, end, html):
    typeof = type(html)
    return map(getattr(typeof, 'strip'), _extract_all(begin, end, html))


def _extract_all(begin, end, html):
    if not html:
        return ''
    result = []
    from_pos = 0
    while True:
        start = html.find(begin, from_pos)
        if start >= 0:
            start += len(begin)
            endpos = html.find(end, start)
            if endpos >= 0:
                result.append(html[start:endpos])
                from_pos = endpos+len(end)
                continue
        break
    return result


def line_strip(txt):
    if not txt:
        return ''
    txt = txt.replace('　', ' ').split('\n')
    return '\n'.join(i for i in [i.strip() for i in txt] if i)


def extract_strip(begin, end, html):
    if not html:
        return ''
    t = extract(begin, end, html)
    if t:
        return strip_line(t)


def extract_map(begin, end, html, func):
    txt = []
    result = []
    prepos = None
    preend = 0
    len_end = len(end)
    len_begin = len(begin)
    while True:
        if prepos is None:
            pos = html.find(begin)
        else:
            pos = html.find(begin, prepos)
        if pos >= 0:
            endpos = html.find(end, pos)
        if pos < 0 or end < 0:
            result.append(html[preend:])
            break
        endpos = endpos+len_end
        result.append(html[preend:pos])
        tmp = func(html[pos:endpos])
        if tmp:
            result.append(tmp)
        prepos = pos+len_begin
        preend = endpos
    return ''.join(result)


if __name__ == '__main__':
    import _env
    from model.po.blog import Po
    from z42.lib.base.txt2html import txt_withlink
    txt = Po.mc_get(10501881)
    txt_withlink(txt.txt)
