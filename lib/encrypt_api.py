#!/usr/bin/env python
# -*- coding:utf-8 -*-

import uuid

def gen_uuid_32():
    return str(uuid.uuid4()).replace('-', '')
