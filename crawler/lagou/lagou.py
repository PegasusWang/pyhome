#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""自己投简历用的，用来拿到lagou职位符合预期地理位置的职位信息"""

import _env
import collections
import re
import json
import requests
from bs4 import BeautifulSoup
from async_spider import AsySpider
from web_util import parse_curl_str
from functools import wraps


def retry(times=3):
    """requests retry decorator"""
    def _retry(func):
        @wraps(func)
        def _wrapper(*args, **kwargs):
            index = 0
            while index < times:
                index += 1
                try:
                    response = func(*args, **kwargs)
                    if response.status_code != 200:
                        print('retry', index)
                        continue
                    else:
                        break
                except Exception as e:
                    print(e)
                    response = None
            return response
        return _wrapper
    return _retry


@retry(3)
def fetch_json(url, data, headers):
    return requests.post(url, data=data, headers=headers)  # use data


def parse_json(s):
    """拿到每页请求得到的职位列表"""
    content = json.loads(s).get('content')
    result = content.get('positionResult').get('result')
    for each in result:
        yield each.get('positionId')


def get_all_urls():
    res = []
    for page in range(1, 30):
        lagou_str = """
        curl 'http://www.lagou.com/jobs/positionAjax.json?city=%E5%8C%97%E4%BA%AC&needAddtionalResult=false' -H 'Cookie: tencentSig=7125489664; user_trace_token=20160425192327-031ce0e3075345a78ae06025f639b168; LGUID=20160425192327-21b06b83-0ad8-11e6-9d60-525400f775ce; ctk=1468641740; JSESSIONID=7FF0D2C2298B22582ACBB807C035AAA2; LGMOID=20160716120220-D5B70628E98E5A204FD0C6112C770633; _gat=1; PRE_UTM=; PRE_HOST=; PRE_SITE=; PRE_LAND=http%3A%2F%2Fwww.lagou.com%2F; index_location_city=%E5%8C%97%E4%BA%AC; SEARCH_ID=8549ce4a6dfd4f3e87db40bc5b1291d2; _ga=GA1.2.1486841592.1461583315; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1468641738; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1468641749; LGSID=20160716120223-19e38457-4b0a-11e6-bb84-525400f775ce; LGRID=20160716120234-208876f0-4b0a-11e6-b12b-5254005c3644' -H 'Origin: http://www.lagou.com' -H 'X-Anit-Forge-Code: 0' -H 'Accept-Encoding: gzip, deflate' -H 'Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4' -H 'User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36' -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' -H 'Accept: application/json, text/javascript, */*; q=0.01' -H 'Referer: http://www.lagou.com/jobs/list_python?labelWords=&fromSearch=true&suginput=' -H 'X-Requested-With: XMLHttpRequest' -H 'Connection: keep-alive' -H 'X-Anit-Forge-Token: None' --data 'first=true&pn={}&kd=python' --compressed
        """.format(page)
        print(lagou_str)
        url, headers, data = parse_curl_str(lagou_str)
        r = fetch_json(url, data=data, headers=headers)  # loads
        if r and r.status_code == 200:
            res.extend(parse_json(r.text))

    position_url = 'http://www.lagou.com/jobs/%s.html'
    return (position_url % str(_id) for _id in res)

C = collections.Counter()


class PositionPageSpider(AsySpider):
    sleep = 3
    def choose_loc(self, url, html):
        # soup = BeautifulSoup(html, 'lxml')
        position = re.search(r"positionAddress = '(.*?)'", html).group(1)
        if '海淀' in position:
            print(url)
            print(position)

    def py_word_count(self, url, html):
        """处理每个页面的方法"""
        html = html.lower()
        for word in ['tornado', 'django', 'flask', 'Pyramid', 'Pylons', 'paste',
                     'gevent', 'twist', 'celery', 'bottle', 'cherrypy', 'pylon',
                     'TurboGears', 'klein', 'web.py', 'zope', 'grok', 'web2py',
                     'cubic', 'wheezy', '爬虫', 'requests', 'scrapy']:
            if word.lower() in html:
                C[word] += 1

    def handle_html(self, url, html):
        print(url)
        self.py_word_count(url, html)


def test_get_all_urls():
    res = list(get_all_urls())
    print(len(res))
    for i in res:
        print(i)
    print(len(res))


if __name__ == '__main__':
    urls = list(get_all_urls())
    s = PositionPageSpider(urls)
    s.run()
    for k, v in C.most_common():
        print(k, v)
