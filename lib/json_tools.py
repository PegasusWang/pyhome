#!/usr/bin/env python
# -*- coding:utf-8 -*-


def bson_to_json(data):
    """trans mongo bson to json, trans ObjectId to str id
    data is a dict return by mongo
    """
    try:
        data['id'] = str(data['_id'])
        del data['_id']
        return data
    except:
        return data
