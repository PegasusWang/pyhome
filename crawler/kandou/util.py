#!/usr/bin/env python
# -*- coding:utf-8 -*-


import _env
from qiniu import Auth, put_data, put_file, etag, urlsafe_base64_encode
from qiniu.compat import StringIO
from web_util import download_file, Downloader, parse_curl_str
from config.config import CONFIG


class KankanDouDownloader(Downloader):
    curl_str = """
    curl 'http://kankandou.com/book/view/12678.html' -H 'Accept-Encoding: gzip, deflate, sdch' -H 'Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4' -H 'Upgrade-Insecure-Requests: 1' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'Referer: http://kankandou.com/login.html?uri=/book/view/12678.html' -H 'Cookie: cisession=2b040f9878b9a9e464e56bf831c3565d8e637e79; CNZZDATA1000201968=2121606612-1470262708-%7C1471877794; Hm_lvt_f805f7762a9a237a0deac37015e9f6d9=1471532383,1471532385,1471534944,1471681547; Hm_lpvt_f805f7762a9a237a0deac37015e9f6d9=1471881503' -H 'Connection: keep-alive' -H 'Cache-Control: max-age=0' --compressed
    """
    url, headers, data = parse_curl_str(curl_str)

    def get(self, *args, **kwargs):
        kwargs.setdefault('headers', self.headers)
        return super(KankanDouDownloader, self).get(*args, **kwargs)


def main():
    url = 'http://kankandou.com/download/file/12678/6044.html'
    d = KankanDouDownloader(url)
    data = d.get_content()

    u = QiniuUploder()
    ret, info = u.put_data('中文.mobi', data)
    import pprint
    pprint.pprint(ret)
    pprint.pprint(info)


class QiniuUploder(object):
    def __init__(self, access_key=CONFIG.QINIU.ACCESS_KEY,
                 secret_key=CONFIG.QINIU.SECRET_KEY,
                 bucket_name=CONFIG.QINIU.BUCKET_NAME,
                 token_timeout=3600):
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name
        self.auth = Auth(access_key, secret_key)
        self.token_timeout = token_timeout

    def put_file(self, key, filepath):
        """ put_file

        :param key: filename in qiniu, key can be chinese
        """
        token = self.auth.upload_token(
            self.bucket_name, key, self.token_timeout
        )
        ret, info = put_file(token, key, filepath)
        return ret, info

    def put_data(self, key, data):
        """ put_data

        :param key: filename in qiniu
        :param data: 二进制流
        """
        token = self.auth.upload_token(
            self.bucket_name, key, self.token_timeout
        )
        ret, info = put_data(token, key, data)
        return ret, info


if __name__ == '__main__':
    main()
