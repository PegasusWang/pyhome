#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from proj.celery import app


import requests


@app.task
def crawl_task(url):
    r = requests.get(url, timeout=3)
    return r
