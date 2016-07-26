#!/usr/bin/env python
# -*- coding: utf-8 -*-


from web_util import get
from html_parser import Bs4HtmlParser


class XiciHtmlParser(Bs4HtmlParser):
    # url = 'http://www.xicidaili.com/'
    def parse(self):
        bs = self.bs
        table_tag = bs.find('table', id='ip_list')
        tr_tags = table_tag.find_all('tr')
        for tr_tag in tr_tags:
            td_tags = tr_tag.find_all('td')
            if td_tags:
                print(td_tags)
                ip, port = td_tags[1].get_text(), td_tags[2].get_text()
                print(ip, port)


def test():
    url = 'http://www.xicidaili.com/nn'
    html = get(url).text
    x = XiciHtmlParser(url, html)
    x.parse()



if __name__ == '__main__':
    test()
