[title]两个学习python tornado的资料
今天介绍的是tornado的文档，tornado是一个高性能的python web框架，和django和flask比起来最大的优势就是支持异步http服务。之前笔者写过几篇使用tornado写的异步爬虫，使用了tornado httpclient模块的AsyncHTTPClient类，爬虫速度相当不错。tornado可以做什么呢？我们可以用来写restful api，用异步特性写高性能的爬虫, 还可以写web应用等。国内的『知乎』应该就是tornado使用的典型吧。下边一一举例子看看tornado可以做什么。

###写个简单的hello world

```
#!/usr/bin/env python
# -*- coding:utf-8 -*-
import tornado.ioloop
import tornado.web


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
    
```
上边示例来自tornado官网，只用几行就是实现了用tornado的web模块写了一个简单的返回hello world的应用。

###tornado的restful接口示例

```
from tornado.web import RequestHandler
from tornado.escape import json_encode


class RestHandler(RequestHandler):

    def write_json(self, data_dict):
        """根据是否含有callback请求参数自动返回json或者jsonp调用"""
        callback = self.get_query_argument('callback', None)

        if callback is not None:    # jsonp
            jsonp = "{jsfunc}({json});".format(jsfunc=callback,
                                               json=json_encode(data_dict))
            self.write(jsonp)    # call set_header after call write
            self.set_header("Content-Type", "application/javascript; charset=UTF-8")
        else:   # json
            self.write(data_dict)
            self.set_header("Content-Type", "application/json; charset=UTF-8")

```
tornado可以写一些restful风格api，比如上边这个示例根据请求参数是不是有callback返回json或者jsonp调用。

###tornado写异步爬虫示例

```
#!/usr/bin/env python
# -*- coding:utf-8 -*-


from datetime import timedelta
from bs4 import BeautifulSoup
from tornado.httpclient import AsyncHTTPClient
from tornado import ioloop, gen, queues


@gen.coroutine
def fetch(url):
    print('fetcing', url)
    response = yield AsyncHTTPClient().fetch(url, raise_error=False)
    raise gen.Return(response)

_q = queues.Queue()


@gen.coroutine
def run():
    try:
        url = yield _q.get()
        res = yield fetch(url)
        html = res.body
        soup = BeautifulSoup(html)
        print(str(soup.find('title')))
    finally:
        _q.task_done()


@gen.coroutine
def worker():
    while not _q.empty():
        yield run()


@gen.coroutine
def main():
    for i in range(73000, 73100):    # 放100个链接进去
        url = "http://www.jb51.net/article/%d.htm" % i
        yield _q.put(url)
    for _ in range(100):    # 模拟100个线程
        worker()
    yield _q.join(timeout=timedelta(seconds=30))


if __name__ == '__main__':
    ioloop.IOLoop.current().run_sync(main)
```
这是笔者之前写过的一个没有节操的爬虫，使用了异步的AsyncHTTPClient类，速度相当不错。

今天给大家推荐的就是tornado的官方文档和一本名字叫做《Introduction to Tornado》的书，目前市面上基本没有其他好的学习tornado的资料，笔者也是看了这两个入了个门。想学习tornado的童鞋可以拿去参考下，也可以去github搜一搜用tornado写的web应用学习下。