[title]python如何用协程模拟线程
之前贴过一个tornado改写的爬虫示例[脚本之家全站文章爬虫](http://pyhome.org/jb51-spider-python/)，可能有些python初学者看得有点头晕。其实笔者学python也不久，协程一直没太能理解，从tornado示例改写成这个爬虫类的时候碰到了很多问题，最不能理解的就是为什么那个异步爬虫可以模拟出并发来。这次又重新回顾了一下，加深了理解。下边就解释一下。之所以使用异步爬虫而不是多线程爬虫，是因为线程开销比较大，开多了线程会导致切换变慢，而且一般线程占用资源也比较多，虽然多线程处理IO密集型任务还是可以提升很多效率的，但是处理网络请求的时候还是倾向于用异步机制。

###协程模拟线程的例子
先看一个简单的例子，来自《Python Cookbook》，这本书会在[书籍](http://pyhome.org/tag/book/)里分享。

```
#!/usr/bin/env python3

def countdown(n):
    while n > 0:
        print('T-minus', n)
        yield
        n -= 1
    print("Blastoff!")


def countup(n):
    x = 0
    while x < n:
        print('Counting up', x)
        yield
        x += 1

from collections import deque

class TaskScheduler:
    def __init__(self):
        self._task_queue = deque()

    def new_task(self, task):
        """Admit a newly started task to the scheduler"""
        self._task_queue.append(task)

    def run(self):
        """run until there are no more tasks"""
        while self._task_queue:
            task = self._task_queue.popleft()
            try:
                # Run until the next yield statement
                next(task)
                self._task_queue.append(task)
            except StopIteration:
                # Generator is no longer executing
                pass


def main():
    sched = TaskScheduler()
    sched.new_task(countdown(10))
    sched.new_task(countdown(5))
    sched.new_task(countup(15))
    sched.run()


if __name__ == '__main__':
    main()

```
这里只有两个协程和一个调度类，执行这段代码以后，有如下输出：

```
('T-minus', 10)
('T-minus', 5)
('Counting up', 0)
('T-minus', 9)
('T-minus', 4)
('Counting up', 1)
('T-minus', 8)
('T-minus', 3)
('Counting up', 2)
('T-minus', 7)
('T-minus', 2)
('Counting up', 3)
('T-minus', 6)
('T-minus', 1)
('Counting up', 4)
('T-minus', 5)
Blastoff!
('Counting up', 5)
('T-minus', 4)
('Counting up', 6)
('T-minus', 3)
('Counting up', 7)
('T-minus', 2)
('Counting up', 8)
('T-minus', 1)
('Counting up', 9)
Blastoff!
('Counting up', 10)
('Counting up', 11)
('Counting up', 12)
('Counting up', 13)
('Counting up', 14)

```
看起来是不是很像开了三个线程在并发执行的结果，但实际上却是一个线程。这里没有使用系统线程，而是用协程来模拟线程，又叫做用户级线程或者绿色线程。解释器遇到yield会挂起执行，在任务调度器类里TaskScheduler用队列进行任务切换，就模拟出了线程的效果。可见，用协程模拟线程主要在于如何调度和驱动这些coroutine的执行。

###怎么用tornado写一个高性能异步爬虫
之前写的那个小爬虫用来处理10万级以下的页面完全没有太大压力，现在就来一步一步试试怎么写出来。
先来看怎么用tornado写抓一个网页的例子:

```
#!/usr/bin/env python
# -*- coding:utf-8 -*-

from tornado import gen
import tornado.httpclient
import tornado.ioloop

@gen.coroutine
def main():
    http_client = tornado.httpclient.AsyncHTTPClient()
    response = yield http_client.fetch('http://httpbin.org/get')
    print(response.body)

tornado.ioloop.IOLoop.current().run_sync(main)
```
当然你也可以试试python3.5的async/await语法。写成下边这样子:

```
#!/usr/bin/env python3.5
# -*- coding:utf-8 -*-

from tornado import gen
import tornado.httpclient
import tornado.ioloop


async def main():
    http_client = tornado.httpclient.AsyncHTTPClient()
    response = await http_client.fetch('http://httpbin.org/get')
    print(response.body)

tornado.ioloop.IOLoop.current().run_sync(main)
```
这里的run_sync方法启动IOLoop，运行传入的函数，然后结束loop。
照着这个思路，如果有很多网页需要抓，我们需要抓取、解析等函数，同样使用异步的httpclient，
首先是用异步AsyncHTTPClient发请求得到一个response对象。
```
from tornado.httpclient import AsyncHTTPClient
from tornado import ioloop, gen, queues
@gen.coroutine
def fetch(url):
    print('fetcing', url)
    response = yield AsyncHTTPClient().fetch(url, raise_error=False)
    raise gen.Return(response)
```
这里使用了装饰器gen.coroutine，我们知道协程对象需要先send(None)或者用next()方法『启动』一下，下边就是个简单的coroutine实现（只是为了说明coroutine工作原理，和爬虫示例无关）

```
def coroutine(func):
    def start(*args, **kwargs):
        rc = func(*args, **kwargs)
        rc.next()
        return rc
    return start
```
现在有了一个异步httpclient发请求了，还要干啥呢，当然是拿到请求的结果然后处理了。

```
from bs4 import BeautifulSoup
_q = queues.Queue()    # tornado.queues

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

```
这里依旧很简单，这个run方法从队列里拿到url并发送请求（注意这个队列是tornado提供的支持协程的队列），得到页面的html，这里用bs4库抠出来title标签。接下来是一个worker，

```
@gen.coroutine
def worker():
    while True:
        yield run()
```
为什么需要一个worker呢，我们需要抓取的过程一直能够进行，直到队列为空为止，这里的worker就是个死循环，一直yield任务。最后写一个main函数执行:

```
@gen.coroutine
def main():
    for i in range(73000, 73100):
        url = "http://www.jb51.net/article/%d.htm" % i
        _q.put(url)
    for _ in range(10):    # 跑十个，十个worker一直从队列取任务执行
        worker()
    yield _q.join(timeout=timedelta(seconds=30))


if __name__ == '__main__':
    ioloop.IOLoop.current().run_sync(main)
```

下边是完整代码:

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
    while True:
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
不到50行的代码一个速度还不错的小爬虫就出来了。你也可以把『并发数量』10改成100，可以看见几乎一瞬间100个网页就解析出来了，真他喵的强悍。

####练习
给读者一个练习，尝试把这个简单的示例改成一个可以重用的类，把发请求，处理页面等拆出来以便子类可以重写这些常见的爬虫操作。还可以使用motor等异步库把得到的结果存储到mongodb数据库里。

