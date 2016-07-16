#!/usr/bin/env python
# -*- coding:utf-8 -*-

import _env
import requests
from web_util import parse_curl_str



s = """curl 'http://www.oanda.com/lang/cns/currency/historical-rates/update?quote_currency=USD&end_date=2016-1-27&start_date=1990-1-1&period=weekly&display=absolute&rate=0&data_range=c&price=mid&view=graph&base_currency_0=CNY&base_currency_1=&base_currency_2=&base_currency_3=&base_currency_4=&' -H 'Cookie: price=mid; period=weekly; data_range=c; mru_base1=EUR%2CUSD%2CGBP%2CCAD%2CAUD; mru_base2=EUR%2CUSD%2CGBP%2CCAD%2CAUD; mru_base3=EUR%2CUSD%2CGBP%2CCAD%2CAUD; mru_base4=EUR%2CUSD%2CGBP%2CCAD%2CAUD; mru_quote=EUR%2CUSD%2CGBP%2CCAD%2CAUD; mru_base0=CNY%2CEUR%2CUSD%2CGBP%2CCAD; base_currency_0=CNY; start_date=1990-01-01; end_date=2016-01-27; opc_id=DE9419D4-C4CA-11E5-94D8-9567B63EDD35; optimizelyEndUserId=oeu1453881134343r0.5306167961098254; optimizelySegments=%7B%22225865993%22%3A%22gc%22%2C%22227082520%22%3A%22direct%22%2C%22227082521%22%3A%22false%22%2C%222289461220%22%3A%22none%22%7D; optimizelyBuckets=%7B%7D; tc=1; _ga=GA1.2.1415034805.1453881137; _gat=1; __atuvc=1%7C4; __atuvs=56a8772e2a63f487000; hcc_session=1453881398' -H 'Accept-Encoding: gzip, deflate, sdch' -H 'Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.82 Safari/537.36' -H 'Accept: text/javascript, text/html, application/xml, text/xml, */*' -H 'Referer: http://www.oanda.com/lang/cns/currency/historical-rates/' -H 'X-Requested-With: XMLHttpRequest' -H 'Connection: keep-alive' -H 'X-Prototype-Version: 1.7' --compressed"""
url, headers, data = parse_curl_str(s)

print(requests.get(url, headers=headers, data=data).content)
