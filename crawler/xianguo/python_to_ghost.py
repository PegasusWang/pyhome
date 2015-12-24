#!/usr/bin/env python
# -*- coding:utf-8 -*-

import _env
import json
import re
import time
from html2text import html2text
from extract import extract
from lib._db import get_collection
from judge_upload import exist_or_insert
from config.config import CONFIG
DB = CONFIG.MONGO.DATABASE


def is_python_article(data_dict):
    title = data_dict.get('title').lower()
    content = data_dict.get('content').lower()
    if ('python' in title) or (content.count('python') > 2):
        return True
    return False


def get_first_img(html):
    img_url = extract('<img src="', '"', html)
    if img_url and len(img_url) > 1800:
        return None
    return img_url


def cur_timestamp():
    return int(time.time() * 1000)


def add_source(content, url, source):
    ori_url = '<a href="%s">来自〔%s〕</a>' % (url, source)
    return content + ori_url


USERS = [
    {
        "id":           1,
        "name":         "jishushare",
        "slug":         "jishushare",
        "email":        "user@example.com",
        "image":        None,
        "cover":        None,
        "bio":          None,
        "website":      None,
        "location":     None,
        "accessibility": None,
        "status":       "active",
        "language":     "zh_CN",
        "meta_title":   None,
        "meta_description": None,
        "last_login":   None,
        "created_at":   1283780649000,
        "created_by":   1,
        "updated_at":   1286958624000,
        "updated_by":   1
    }
]


TAGS = [
    {
        "id": 4000,
        "name": u"订阅",
        "slug": u"subscribe",
        "description": ""
    }
]
TAG_ID_MAP = {}


def gen_tag_id():
    tag_li = PROGRAM_ID.split('\n')
    for i in tag_li:
        tag = i.split()[0]
        tag_id = int(i.split()[-1])
        TAG_ID_MAP[tag] = tag_id

    for tag, tag_id in TAG_ID_MAP.items():
        TAGS.append(
            {
                "id": tag_id,
                "name": tag,
                "slug": tag,
                "description": ""
            }
        )

def replace_post(post_data):
    d = {
        "id": 5,
        "title":        "my blog post title",
        "slug":         "my-blog-post-title",
        "markdown":     "",
        #"html":         "the <i>html</i> formatted post body",
        "image":        None,
        "featured":     0,
        "page":         0,
        "status":       "published",
        "language":     "zh_CN",
        "meta_title":   None,
        "meta_description": None,
        "author_id":    1,
        "created_at":   cur_timestamp(),
        "created_by":   1,
        "updated_at":   cur_timestamp(),
        "updated_by":   1,
        "published_at": cur_timestamp(),
        "published_by": 1
    }
    d['id'] = int(str(post_data['_id']))
    d['title'] = post_data['title'].strip()
    d['slug'] = post_data['title'].strip().replace(' ', '-')

    html = post_data['content'].strip()
    d['image'] = get_first_img(html)
    d['markdown'] = add_source(html, post_data['url'], post_data['source'])
    d['published_at'] = int(post_data['time']) * 1000
    return d


def migrate(coll_name, limit=10):
    coll = get_collection(DB, coll_name)
    # gen_tag_id()    # gen tag first
    res = {
        "meta": {
            "exported_on": cur_timestamp(),
            "version": "003"
        }
    }

    posts = []
    posts_tags = []
    index = 0

    slug_set = set()
    for doc in coll.find().sort('time', -1).batch_size(1000):
        if is_python_article(doc):
            title = doc.get('title')
            if not exist_or_insert(title):
                doc_id = doc.get('_id')
                index += 1
                if index > limit:
                    break
                slug = doc.get('title')
                if len(slug) > 30:
                    slug = slug[0:30]
                doc['title'] = slug
                if slug not in slug_set:
                    slug_set.add(slug)
                    posts.append(replace_post(doc))
                    posts_tags.append(
                        {"tag_id": TAGS[0].get('id'), "post_id": int(doc_id)}
                    )

    data = {
        "posts": posts,
        "tags": TAGS,
        "posts_tags": posts_tags,
        "users": USERS
    }
    res["data"] = data
    return res


def main():
    import sys
    try:
        cnt = int(sys.argv[1])
    except:
        cnt = 20
    res = migrate('python', cnt)
    print(json.dumps(res, indent=4))


if __name__ == '__main__':
    main()
