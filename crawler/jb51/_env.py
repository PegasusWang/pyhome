#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from os.path import abspath, dirname, join

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

PREFIX = abspath(
    join(
        dirname(abspath(__file__)), '../'
    )
)

PARENT = abspath(
    join(
        dirname(abspath(__file__)), '../../'
    )
)

if PREFIX not in sys.path:
    sys.path.append(PREFIX)
    sys.path.append(PARENT)
