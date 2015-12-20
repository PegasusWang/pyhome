写一个简单的python爬虫入门教程吧，笔者目前也比较菜，但是还是希望把学到的一些知识分享下。
###什么是爬虫?为什么要写爬虫？
爬虫就是可以发送http请求得到请求页面内容的一些程序，因为互联网的网状结构，爬虫可以有深度优先和宽度优先爬取策略，这根图论里边学到的深搜和广搜是一样的。像是google、baidu等搜索引擎就会有自己的爬虫每天从互联网收集海量的信息。当然我们自己写的小爬虫就是从互联网收集信息用的，爬虫也是一种比较廉价的方式。比如这一篇爬取脚本之家的爬虫[脚本之家全站技术文章爬虫](http://pyhome.org/jb51-spider-python/)，只需要很少的代码就能在短时间内搞到很多内容。如你所见，这个站点很多文章就是爬虫抓过来的。

###知识准备
写爬虫一般涉及到几个过程，发请求抓取->解析页面->存储->数据处理等过程。涉及到的知识包括http协议，html，数据库，数据处理等知识，先用一个小工具curl讲一下。(希望你是用的是linux或者mac)

###爬虫过程
这里用curl讲一下，CURL是一个利用URL语法在命令行下工作的文件传输工具。在terminal下用

`curl http://pyhome.org/`

然后就能在终端下唰唰地返回python之家首页的html啦。这就是发送请求的过程，接下来是爬虫需要做的是解析过程，这里我们用grep命令取出title

`curl http://pyhome.org/ | grep '<title>'`

然后就能看到所有包含'title'字符串的行被取出来了，这和爬虫中用一些库『抠』出来html页面中的内容很类似。接下来一般是存储，我们也可以用一个命令来模拟。

`curl http://pyhome.org/ | grep 'title' > t.txt`

一般爬虫存储到mysql，mongodb等数据库，这里用命令直接重定向到"t.txt"这个文本文件，也是存储下来了。
可以看到，最后一个长命令差不多就是简单的爬虫了，从抓取到抠内容到存储，一个简单的爬虫就这么模拟了。

###python爬虫
上面只是说了curl模拟的爬虫，一般爬虫都比这个复杂多了，这就需要用到python各种功能强悍的库，每个过程都有很多库可以选择。

1. 请求过程（发送GET或者POST请求)。urllib,urllib2, requests, grequests,tornado的httpclient和异步AsyncHTTPClient,python3的aiohttp等等。
2. 解析html。有lxml，beautifulsoup，pyquery等。
3. 存储。用到mysql，mongodb等数据库的python驱动。

当然还有scrapy这种好用的爬虫框架。
每个库的使用都可以直接google到官方文档查看，不过我这种收藏癖还是都下载了电子版。

###爬取本博客的一个爬虫示例
网上好多爬虫示例都是啥这妹子那妹子的爬虫，笔者也搞过，爬了tumblr一百多万张妹子图，快肾虚了，还搞了一个小网站[今日图片](http://jinritu.com)，少年慎入。这里就以把这篇博客爬下来并保存为例，写一个简单的爬虫。（这个平台使用的是nodejs开发的博客系统ghost，没有什么爬虫防护措施。）仍以基本的抓取、解析、存储三个过程示例，就只有几行简单的代码。

```

#!/usr/bin/env python2.7
# -*- coding:utf-8 -*-

import io
import json
import requests
from bs4 import BeautifulSoup


def fetch(url):
    """fetch and return html"""
    return requests.get(url).text


def parse_html(html):
    """get data from html, return data as a dict"""
    soup = BeautifulSoup(html)
    title = unicode(soup.find(class_='post-title'))
    content = unicode(soup.find(class_='post-content'))
    return {
        'title': title,
        'content': content
    }


def save(url, data):
    """save data as json file"""
    filename = url.rstrip('/').rsplit('/', 1)[1] + '.json'
    with io.open(filename, 'w+', encoding='utf8') as outfile:
        data = json.dumps(data, ensure_ascii=False, encoding='utf8', indent=4)
        outfile.write(unicode(data))


def main():
    url = 'http://pyhome.org/jb51-spider-python/'
    html = fetch(url)
    data = parse_html(html)
    save(url, data)


if __name__ == '__main__':
    main()


```

###练习
这里给读者一个小的练习，阅读requests和beautifulsoup4的文档，爬取并保存Python之家的所有文章，大概几千篇吧，保存到你本地。

你需要想想以下几个问题：

- 怎么才能找到这个站点所有的文章链接？
- 如何处理一些http异常状态，比如404，500，599？
- 有没有碰到编码问题？（python2和3的区别）
- 爬取效率如何？
- 怎样加速(多线程、异步）？
- 代码可以封装成一个类用来重用吗？
- 你是打算用简单的for循环还是用队列来处理呢？

###参考
之前给出的文档就不列举了，这里给大家推荐OReilly的一本英文python爬虫书。《Web Scraping with Python》。从基础到进阶基本都有，包括反爬虫策略，解决js动态生成页面等。
