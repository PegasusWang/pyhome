#!/usr/bin/env python
# -*- coding: utf-8 -*-

import _env
from config.config import CONFIG
from pymongo import MongoClient
# from motor import MotorClient
from redis import StrictRedis


mongo_client = MongoClient(CONFIG.MONGO.HOST, CONFIG.MONGO.PORT)
# motor_client = MotorClient(CONFIG.MONGO.HOST, CONFIG.MONGO.PORT)
redis_client = StrictRedis(CONFIG.REDIS.HOST, CONFIG.REDIS.PORT)


client_db_map = {
    'mongo': mongo_client,
    # 'motor': motor_client
}


def get_collection(db_name, collection_name, client='mongo'):
    client = client_db_map.get(client)
    db = getattr(client, db_name, None)
    return getattr(db, collection_name, None)


def get_db(db_name, client='mongo'):
    client = client_db_map.get(client)
    return getattr(client, db_name, None)
