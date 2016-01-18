#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
chrome有个功能，对于请求可以直接右键copy as curl，然后在命令行里边用curl
模拟发送请求。现在需要把此curl字符串处理成requests库可以传入的参数格式，
http://stackoverflow.com/questions/23118249/whats-the-difference-between-request-payload-vs-form-data-as-seen-in-chrome
"""

import json
import re
import requests


def encode_to_dict(encoded_str):
    """ 将encode后的数据拆成dict
    >>> encode_to_dict('name=foo')
    {'name': foo'}
    >>> encode_to_dict('name=foo&val=bar')
    {'name': 'foo', 'val': 'var'}
    """

    pair_list = encoded_str.split('&')
    d = {}
    for pair in pair_list:
        if pair:
            key = pair.split('=')[0]
            val = pair.split('=')[1]
            d[key] = val
    return d


def parse_curl_str(s):
    """convert chrome curl string to url, headers dict and data"""
    pat = re.compile("'(.*?)'")
    str_list = [i.strip() for i in re.split(pat, s)]   # 拆分curl请求字符串

    url = ''
    headers = {}
    data = ''

    for i in range(0, len(str_list)-1, 2):
        arg = str_list[i]
        string = str_list[i+1]

        if arg.startswith('curl'):
            url = string

        elif arg.startswith('-H'):
            header_key = string.split(':', 1)[0].strip()
            header_val = string.split(':', 1)[1].strip()
            headers[header_key] = header_val

        elif arg.startswith('--data'):
            data = string

    return url, headers, data


def test_lagou():
    lagou_str = """curl 'http://www.lagou.com/jobs/positionAjax.json?gj=1-3%E5%B9%B4&px=default&city=%E5%8C%97%E4%BA%AC' -H 'Cookie: user_trace_token=20150911115414-e35eaafdf3cd430fb0a9fed4ca568273; LGUID=20150911115415-c53a987d-5838-11e5-8fa5-525400f775ce; fromsite=www.baidu.com; LGMOID=20160112143105-A2EDC0F26EF4FF9F7A0E261E95FFC0D5; tencentSig=5171360768; JSESSIONID=0F7B9502EFBBC658FD043C42196C5F58; PRE_UTM=; PRE_HOST=; PRE_SITE=http%3A%2F%2Fwww.lagou.com%2Fjobs%2F1018226.html; PRE_LAND=http%3A%2F%2Fwww.lagou.com%2Fjobs%2F1018226.html; login=true; unick=%E7%8E%8B%E5%AE%81%E5%AE%81-Python%E5%BA%94%E8%81%98; showExpriedIndex=1; showExpriedCompanyHome=1; showExpriedMyPublish=1; hasDeliver=77; SEARCH_ID=c70df91703ee4c1ca380d883e93dde6c; index_location_city=%E5%8C%97%E4%BA%AC; _gat=1; HISTORY_POSITION=1326282%2C9k-18k%2C%E4%BB%80%E4%B9%88%E5%80%BC%E5%BE%97%E4%B9%B0%2CPython%7C1247829%2C8k-16k%2CPair%2CPython%7C1162119%2C8k-15k%2C%E5%A4%A7%E7%A0%81%E7%BE%8E%E8%A1%A3%2CPython%E5%B7%A5%E7%A8%8B%E5%B8%88%7C411250%2C10k-20k%2C%E6%9C%89%E5%BA%B7%E7%88%B1%E5%B8%AE%2CPython%20%E5%BC%80%E5%8F%91%E5%B7%A5%E7%A8%8B%E5%B8%88%7C1269616%2C12k-20k%2CE%E7%98%A6%E7%BD%91%2CPython%7C; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1452172939,1452231058,1452231062,1452580269; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1453095567; LGSID=20160118132416-b7c3fc3c-bda3-11e5-8bf5-5254005c3644; LGRID=20160118133926-d61df46a-bda5-11e5-8a39-525400f775ce; _ga=GA1.2.878965075.1441943655' -H 'Origin: http://www.lagou.com' -H 'Accept-Encoding: gzip, deflate' -H 'Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36' -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' -H 'Accept: application/json, text/javascript, */*; q=0.01' -H 'Referer: http://www.lagou.com/jobs/list_Python?gj=1-3%E5%B9%B4&px=default&city=%E5%8C%97%E4%BA%AC' -H 'X-Requested-With: XMLHttpRequest' -H 'Connection: keep-alive' --data 'first=false&pn=9&kd=Python' --compressed"""
    url, headers, data = parse_curl_str(lagou_str)
    r = requests.post(url, data=data, headers=headers)  # loads
    print(r.content)


if __name__ == '__main__':
    test_lagou()
