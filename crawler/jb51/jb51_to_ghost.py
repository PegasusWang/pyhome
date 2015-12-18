#!/usr/bin/env python
# -*- coding:utf-8 -*-

import _env
import json
import re
import time
from lib._db import get_collection
from config.config import CONFIG
from judge_upload import exist_or_insert
DB = CONFIG.MONGO.DATABASE


PAT = re.compile('[-#\w]+')


def find_first_tag(s):
    m = PAT.search(s)
    return m.group() if m else s


def remove_china_char(s):
    if not s:
        return s
    return re.sub(ur"[\u4e00-\u9fa5]+", '', s)


def cur_timestamp():
    return int(time.time() * 1000)


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
        "id": 1,
        "name": u'文章',
        "slug": u'article',
        "description": ""
    }
]


def replace_post(post_data):
    d = {
        "id": 5,
        "title":        "my blog post title",
        #"slug":         "my-blog-post-title",
        "markdown":     "the *markdown* formatted post body",
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
    d['id'] = int(post_data['source_url'].rsplit('/', 1)[1].split('.')[0])
    d['title'] = post_data['title'].strip()
    if post_data['slug'] > 30:
        d['slug'] = post_data['slug'][0:30]
    d['markdown'] = post_data['content'].strip()
    return d


def migrate(coll_name='article_pyhome', skip=0, limit=10):
    res = {
        "meta": {
            "exported_on": cur_timestamp(),
            "version": "003"
        }
    }
    coll = get_collection(DB, coll_name)

    posts = []
    posts_tags = []
    slug_set = set()

    for doc in coll.find().skip(skip).limit(limit):
        title = doc.get('title')
        slug = title.lower().strip()

        if slug and (slug not in slug_set):
            slug_set.add(slug)
            doc['slug'] = slug

            if not exist_or_insert(slug):
                doc_id = doc.get('_id')
                post_id = int(doc['source_url'].rsplit('/', 1)[1].split('.')[0])

                posts.append(replace_post(doc))
                posts_tags.append(
                    {"tag_id": 1, "post_id": post_id}
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
    coll = get_collection(DB, 'article')

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


def test():
    print(find_first_tag('正则表达式指南'))


def main():
    import sys
    try:
        cnt = int(sys.argv[1])
    except:
        cnt = 300
    res = migrate('article_pyhome', 1000, 1000)
    print(json.dumps(res, indent=4))


if __name__ == '__main__':
    main()
