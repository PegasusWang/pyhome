[title]用python写一个命令行有道词典

平常都是用终端敲， 有时候不会的词语也懒得打开词典了，干脆搞了个简单的查词命令.思路也很简单，直接调用有道的api，解析下返回的json就ok了。只用到了python原生的库，支持python2和python3.

    #!/usr/bin/env python
    # -*- coding:utf-8 -*-

    # API key：273646050
    # keyfrom：11pegasus11

    import json
    import sys

    try:    # py3
        from urllib.parse import urlparse, quote, urlencode, unquote
        from urllib.request import urlopen
    except:    # py2
        from urllib import urlencode, quote, unquote
        from urllib2 import urlopen


    def fetch(query_str=''):
        query_str = query_str.strip("'").strip('"').strip()
        if not query_str:
            query_str = 'python'

        print(query_str)
        query = {
            'q': query_str
        }
        url = 'http://fanyi.youdao.com/openapi.do?keyfrom=11pegasus11&key=273646050&type=data&doctype=json&version=1.1&' + urlencode(query)
        response = urlopen(url, timeout=3)
        html = response.read().decode('utf-8')
        return html


    def parse(html):
        d = json.loads(html)
        try:
            if d.get('errorCode') == 0:
                explains = d.get('basic').get('explains')
                for i in explains:
                    print(i)
            else:
                print('无法翻译')

        except:
            print('翻译出错，请输入合法单词')


    def main():
        try:
            s = sys.argv[1]
        except IndexError:
            s = 'python'
        parse(fetch(s))


    if __name__ == '__main__':
        main()


###使用
1. 将上面代码粘贴后命名为youdao.py
2. 修改名称`mv youdao.py youdao`, 然后加上可执行权限`chmod a+x youdao`
3. 拷贝到/usr/local/bin。 `cp youdao /usr/local/bin`

使用的时候把要翻译的单词作为第一个命令行参数，要是句子用引号括起来。
![效果图](http://7ktuty.com1.z0.glb.clouddn.com/youdao.png)


###How Do Python Coroutines Work?（一个不错的youtube视频教程,来自motor作者Jesse）
<iframe width="420" height="315" src="https://www.youtube.com/embed/7sCu4gEjH5I"
frameborder="0" allowfullscreen></iframe>
