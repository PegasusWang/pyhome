#!/usr/bin/env python
# -*- coding: utf-8 -*-

import _env
from lib._db import get_db
from pprint import pprint as pp
db = get_db('htmldb')
col = getattr(db, 'lagou_html')    # collection


def test_get_db():
    o = col.find_one({'_id':1234})
    html = o['html']
    # print html
    pp(o)
