#!/usr/bin/env python
# -*- coding: utf-8 -*-

import _env
import json
import io
import os
import re
import requests
from lib._db import get_collection
from lib.debug_tools import print_li
from pprint import pprint
from html2text import html2text
from extract import extract as et
from extract import extract_all as et_all
from markdown2 import markdown, markdown_path


def get_all_files(path):
    res = set()
    list_dirs = os.walk(path)
    for root, dirs, files in list_dirs:
        for f in files:
            res.add(os.path.join(root, f))
    return res


def remove_words(s):
    for key in ['<!--NEWSZW_HZH_END-->', '<!--NEWSZW_HZH_BEGIN-->']:
                #'http://www.jb51.net', 'www.jb51.net', 'jb51.net']:
        s = s.replace(key, '')
    return s


def parse_jb51(html):
    """pass original html, decode here"""
    html = et('<div id="contents">', 'class="relatedarticle', html)
    html = html.decode('gb18030', 'ignore')    # gb2312也用gb18030解码
    art_title = et('">', '</h1>', et('<div class="title">', '</div>', html))
    art_brief = et('<div id="art_demo">', '</div>', html)
    art_content = et('<div id="contents">', '</div><!--endmain-->', html)
    if not art_content:
        art_content = et('<div id="content">', '</div><!--endmain-->', html)

    art_tags = [et('">', '<', i) for i in
        list(et_all('<a', '/a>', et('<div class="tags', '</div>', html)))]

    if art_brief:
        art_content = html2markdown(art_brief + '\n' + art_content)
    else:
        art_brief = html2markdown(art_content[0:100] + '… …')
        art_content = html2markdown(art_content)

    art_brief = remove_words(art_brief)
    art_content = remove_words(art_content)

    to_save = {'art_title': 'title',
               'art_brief': 'brief',
               'art_content': 'content',
               'art_tags': 'tag_list',
               }

    d = {}
    for k, v in locals().items():
        if k in to_save:
            key = to_save[k]
            d[key] = v
    return d


def html2markdown(html):
    return html2text(html)


def markdown2html(md):
    """对于代码块\n\n```\n\n + codeblock + \n\n```\n\n"""
    return markdown(md, extras=["code-friendly", 'fenced-code-blocks'])


def all_to_txt(input_path, output_path):
    i = 0
    max_cnt = 10

    all_files = get_all_files(input_path)
    for each in all_files:
        i += 1
        if i > max_cnt:
            break
        with open(each, 'r') as f:
            html = f.read()
            data = parse_jb51(html)

            file_id = os.path.basename(each).rsplit('.', 1)[0]
            data['source'] = 'http://www.jb51.net/article/%s.htm' % file_id
            data['source_id'] = file_id
            filename = os.path.join(output_path, file_id + '.txt')
            print(filename)

            if data.get('brief'):
                print(len(data.get('brief')))
            with io.open(filename, 'w+', encoding='utf-8') as outfile:
                data = json.dumps(data, ensure_ascii=False, encoding='utf-8',
                                  indent=4)

                outfile.write(unicode(data))


def all_to_html(input_path, output_path):
    all_files = get_all_files(input_path)
    for each in all_files:
        if each.endswith('txt'):
            with io.open(each, 'r', encoding='utf-8') as f:
                d = json.load(f)
                md = d.get('content')
                filename = os.path.join(output_path,
                            os.path.basename(each).rsplit('.', 1)[0] + '.html')
                print(filename)
                with io.open(filename, 'w+', encoding='utf-8') as f:
                    f.write(markdown2html(md))


def save_to_mongo(db_name, col_name, doc_path):
    articles = get_collection(db_name, col_name)  # collection articles

    max_cnt = 100
    index = 0

    for path in get_all_files(doc_path):
        print(path)
        index += 1
        if index > max_cnt:
            return

        with open(path, 'r') as f:
            html = f.read()
            data = parse_jb51(html)

            file_id = os.path.basename(path).rsplit('.', 1)[0]
            data['source'] = 'http://www.jb51.net/article/%s.htm' % file_id
            data['source_id'] = file_id

            print(data.get('source_id'))
            print(data.get('title'))

            articles.update(
                {'source_id': data.get('source_id')},
                {
                    '$set': data
                },
                True
            )


def test():
    url = 'http://www.jb51.net/article/74084.htm'
    content = requests.get(url).content
    for k, v in (parse_jb51(content)).items():
        print k, v


if __name__ == '__main__':
    #save_to_mongo('test', 'Articles', '/home/wnn/raw/jb51_html')
    test()
