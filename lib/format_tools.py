#!/usr/bin/env python
# -*- coding:utf-8 -*-


def format_news_list(news_dict_list):
    """返回格式化的news_list.

    Args:
        news_dict_list: news字典列表.
        [
            {
                "url": ''
                "time": ''    # 时间戳int
                "title": ''
                "host": ''
                "docid": ''
            }
            ...
        ]
    Returns:
        member_list: [ [docid, title, url, time, host]...]
    """
    if not news_dict_list:    # empty or None
        return []

    news_list = []
    for news_dict in news_dict_list:
        each_list = []
        for key in ['docid', 'title', 'url', 'time', 'host']:
            if key == 'time':
                try:
                    time_stamp = news_dict.get(key, 0)
                    each_list.append(int(float(time_stamp)))
                except ValueError:
                    each_list.append(0)

            else:
                each_list.append(news_dict.get(key, ''))
        news_list.append(each_list)

    return news_list
