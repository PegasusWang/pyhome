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


# title section_id from xianguo json
TECH_ID = """钛媒体 1410319
创业邦 1057591
36氪 1057676
快鲤鱼 1382170
创业家 1132786
TechCrunch 中国 1847011
小众软件 1000542
极客公园 1250579
爱范儿 1000806
i黑马 1236199
新智派 2271997
瘾科技 1000192
互联网的那点事 1057660
TECH2IPO创见 1059587"""


TAGS = [
    {
        "id": 3000,
        "name": u"新闻",
        "slug": u"news",
        "description": ""
    }
]
TAG_ID_MAP = {}


def gen_tag_id():
    tag_li = TECH_ID.split('\n')
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


def tag_migrate(limit=10):
    res = {
        "meta": {
            "exported_on": cur_timestamp(),
            "version": "003"
        }
    }
    coll = get_collection(DB, 'code')

    posts = []
    tags_id_map = {}
    posts_tags = []
    tag_id = 1000
    index = 0

    for doc in coll.find().batch_size(1000):
        #print(doc.get('title'))
        index += 1
        if index > limit:
            break

        posts.append(replace_post(doc))
        post_id = int(doc['source_url'].rsplit('/', 1)[1].split('.')[0])
        tag_list = doc.get('tag_list')
        tag = tag_list[0] if tag_list else ''
        tag = remove_china_char(tag)
        if tag:
            save_tag = tag.replace(' ', '-').lower()
            save_tag = find_first_tag(save_tag)
            if len(save_tag) > 10:
                posts_tags.append(
                    {"tag_id": 1, "post_id": post_id}
                )
                continue

            if save_tag not in tags_id_map:
                tag_id += 1
                TAGS.append({
                    "id": tag_id,
                    "name": save_tag,
                    "slug": save_tag,
                    "description": ""
                })
                tags_id_map[save_tag] = tag_id
                posts_tags.append(
                    {"tag_id": tags_id_map[save_tag], "post_id": post_id}
                )
            else:
                posts_tags.append(
                    {"tag_id": tags_id_map[save_tag], "post_id": post_id}
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
        cnt = 10
    res = migrate('tech', cnt)
    print(json.dumps(res, indent=4))

if __name__ == '__main__':
    main()
