#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import threading
import time
try:
    from queue import Queue
except ImportError:
    from Queue import Queue

import concurrent.futures
import bs4
import requests
from web_util import logged, get


class Worker(threading.Thread):    # 处理工作请求
    def __init__(self, workQueue, resultQueue, **kwds):
        threading.Thread.__init__(self, **kwds)
        self.setDaemon(True)
        self.workQueue = workQueue
        self.resultQueue = resultQueue

    def run(self):
        while 1:
            try:
                callable, args, kwds = self.workQueue.get(False)    # get task
                res = callable(*args, **kwds)
                self.resultQueue.put(res)    # put result
            except Queue.Empty:
                break


class WorkManager(object):    # 线程池管理,创建
    def __init__(self, num_of_workers=10):
        self.workQueue = Queue.Queue()    # 请求队列
        self.resultQueue = Queue.Queue()    # 输出结果的队列
        self.workers = []
        self._recruitThreads(num_of_workers)

    def _recruitThreads(self, num_of_workers):
        for i in range(num_of_workers):
            worker = Worker(self.workQueue, self.resultQueue)    # 创建工作线程
            self.workers.append(worker)    # 加入到线程队列

    def start(self):
        for w in self.workers:
            w.start()

    def wait_for_complete(self):
        while len(self.workers):
            worker = self.workers.pop()    # 从池中取出一个线程处理请求
            worker.join()
            if worker.isAlive() and not self.workQueue.empty():
                self.workers.append(worker)    # 重新加入线程池中
        print 'All jobs were complete.'

    def add_job(self, callable, *args, **kwds):
        self.workQueue.put((callable, args, kwds))    # 向工作队列中加入请求

    def get_result(self, *args, **kwds):
        return self.resultQueue.get(*args, **kwds)


def download_file(url):
    """这里可以请求并保存网页"""
    # print 'beg download', url
    print requests.get(url).text


def test_work():
    try:
        num_of_threads = int(sys.argv[1])
    except IndexError:
        num_of_threads = 10
    _st = time.time()
    wm = WorkManager(num_of_threads)
    print num_of_threads
    urls = ['http://www.baidu.com'] * 100    # 待爬的url
    for i in urls:
        wm.add_job(download_file, i)
    wm.start()
    wm.wait_for_complete()
    print time.time() - _st


@logged
class ThreadPoolCrawler(object):

    def __init__(self, urls=None, concurrency=20, **kwargs):
        self.urls = urls or []
        if not self.urls:
            self.init_urls()
        self.concurrency = min(concurrency, len(self.urls))
        self.results = []

    def init_urls(self):
        """init_urls: assign url list to self.urls"""
        raise NotImplementedError

    def handle_response(self, url, response):
        print(url)
        print(response.status_code)

    def get(self, *args, **kwargs):
        return get(*args, **kwargs)    # use web_util get

    def run_async(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.concurrency) as executor:
            future_to_url = {
                executor.submit(self.get, url): url for url in self.urls
            }
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    response = future.result()
                except Exception as e:
                    # import traceback
                    # traceback.print_exc()
                    print(e)
                else:
                    self.handle_response(url, response)

    def run_sync(self):
        for url in self.urls:
            try:
                response = self.get(url)
            except Exception as e:
                import traceback
                traceback.print_exc()
            else:
                self.handle_response(url, response)
            if self.sleep:
                time.sleep(self.sleep)

    def run(self, use_thread=True):
        if use_thread:
            self.run_async()
        else:
            self.run_sync()


class TestCrawler(ThreadPoolCrawler):
    def handle_response(self, url, response):
        print(url, response.status_code)
        pass
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        title = soup.find('title')
        self.results.append({url: title})


def main():
    urls = ['http://localhost:8000/test'] * 100
    for nums in [5, 10, 15, 20, 50, 70, 100]:
        beg = time.time()
        s = TestCrawler(urls, nums)
        s.run()
        print(nums, time.time()-beg)


def test():
    # urls = ['http://localhost:8000/test'] * 5
    urls = ['http://www.baidu.com'] * 5
    s = TestCrawler(urls)
    s.run()


if __name__ == '__main__':
    main()
