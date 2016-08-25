#!/usr/bin/env python
# -*- coding:utf-8 -*-

import _env
import datetime
import json
import errno
import re
import urllib2
import threading
import time
import requests
from Queue import Queue
import MySQLdb as mdb
from config.config import CONFIG


DB_HOST = CONFIG.MYSQL.HOST
DB_USER = CONFIG.MYSQL.USER
DB_PASS = CONFIG.MYSQL.PASS


re_start = re.compile(r'start=(\d+)')
re_uid = re.compile(r'query_uk=(\d+)')  # 查询编号
re_urlid = re.compile(r'&urlid=(\d+)')  # url编号

ONEPAGE = 20  # 一页数据量
ONESHAREPAGE = 20  # 一页分享连接量


#缺少专辑列表

URL_SHARE = 'http://yun.baidu.com/pcloud/feed/getsharelist?auth_type=1&start={start}&limit=20&query_uk={uk}&urlid={id}' #获得分享列表

"""

{"feed_type":"share","category":6,"public":"1","shareid":"1541924625","data_id":"2418757107690953697","title":"\u5723\u8bde\u58c1\u7eb8\u5927\u6d3e\u9001","third":0,"clienttype":0,"filecount":1,"uk":1798788396,"username":"SONYcity03","feed_time":1418986714000,"desc":"","avatar_url":"http:\/\/himg.bdimg.com\/sys\/portrait\/item\/1b6bf333.jpg","dir_cnt":1,"filelist":[{"server_filename":"\u5723\u8bde\u58c1\u7eb8\u5927\u6d3e\u9001","category":6,"isdir":1,"size":1024,"fs_id":870907642649299,"path":"%2F%E5%9C%A3%E8%AF%9E%E5%A3%81%E7%BA%B8%E5%A4%A7%E6%B4%BE%E9%80%81","md5":"0","sign":"1221d7d56438970225926ad552423ff6a5d3dd33","time_stamp":1439542024}],"source_uid":"871590683","source_id":"1541924625","shorturl":"1dDndV6T","vCnt":34296,"dCnt":7527,"tCnt":5056,"like_status":0,"like_count":60,"comment_count":19},

public:公开分享

title:文件名称

uk:用户编号

"""

URL_FOLLOW = 'http://yun.baidu.com/pcloud/friend/getfollowlist?query_uk={uk}&limit=20&start={start}&urlid={id}' #获得订阅列表

"""

{"type":-1,"follow_uname":"\u597d\u55e8\u597d\u55e8\u554a","avatar_url":"http:\/\/himg.bdimg.com\/sys\/portrait\/item\/979b832f.jpg","intro":"\u9700\u8981\u597d\u8d44\u6599\u52a0994798392","user_type":0,"is_vip":0,"follow_count":2,"fans_count":2276,"follow_time":1415614418,"pubshare_count":36,"follow_uk":2603342172,"album_count":0},

follow_uname:订阅名称

fans_count：粉丝数

"""

URL_FANS = 'http://yun.baidu.com/pcloud/friend/getfanslist?query_uk={uk}&limit=20&start={start}&urlid={id}' # 获取关注列表

"""

{"type":-1,"fans_uname":"\u62e8\u52a8\u795e\u7684\u5fc3\u7eea","avatar_url":"http:\/\/himg.bdimg.com\/sys\/portrait\/item\/d5119a2b.jpg","intro":"","user_type":0,"is_vip":0,"follow_count":8,"fans_count":39,"follow_time":1439541512,"pubshare_count":15,"fans_uk":288332613,"album_count":0}

avatar_url：头像

fans_uname：用户名

"""



QNUM = 1000
hc_q = Queue(20) #请求队列
hc_r = Queue(QNUM) #接收队列
success = 0
failed = 0


def req_worker(inx): #请求

    s = requests.Session() #请求对象

    while True:

        req_item = hc_q.get() #获得请求项



        req_type = req_item[0] #请求类型，分享?订阅？粉丝？

        url = req_item[1] #url

        r = s.get(url) #通过url获得数据

        hc_r.put((r.text, url)) #将获得数据文本和url放入接收队列

        print "req_worker#", inx, url #inx 线程编号； url 分析了的 url


def response_worker(): #处理工作

    dbconn = mdb.connect(DB_HOST, DB_USER, DB_PASS, 'baiduyun', charset='utf8')

    dbcurr = dbconn.cursor()

    dbcurr.execute('SET NAMES utf8')

    dbcurr.execute('set global wait_timeout=60000') #以上皆是数据库操作

    while True:

        """

        #正则备注

        match() 决定 RE 是否在字符串刚开始的位置匹配

        search() 扫描字符串，找到这个 RE 匹配的位置

        findall() 找到 RE 匹配的所有子串，并把它们作为一个列表返回

        finditer() 找到 RE 匹配的所有子串，并把它们作为一个迭代器返回

                  百度页面链接：http://pan.baidu.com/share/link?shareid=3685432306&uk=1798788396&from=hotrec

        uk 其实用户id值

        """

        metadata, effective_url = hc_r.get() #获得metadata（也就是前面的r.text）和有效的url

        #print "response_worker:", effective_url

        try:

            tnow = int(time.time()) #获得当前时间

            id = re_urlid.findall(effective_url)[0] #获得re_urlid用户编号

            start = re_start.findall(effective_url)[0] #获得start用户编号

            if True:

                if 'getfollowlist' in effective_url: #type = 1，也就是订阅类

                    follows = json.loads(metadata) #以将文本数据转化成json数据格式返回

                    uid = re_uid.findall(effective_url)[0] #获得re_uid，查询编号

                    if "total_count" in follows.keys() and follows["total_count"]>0 and str(start) == "0": #获得订阅数量

                        for i in range((follows["total_count"]-1)/ONEPAGE): #开始一页一页获取有用信息

                            try:

                                dbcurr.execute('INSERT INTO urlids(uk, start, limited, type, status) VALUES(%s, %s, %s, 1, 0)' % (uid, str(ONEPAGE*(i+1)), str(ONEPAGE)))

                                #存储url编号，订阅中有用户编号，start表示从多少条数据开始获取，初始status=0为未分析状态

                            except Exception as ex:

                                print "E1", str(ex)

                                pass



                    if "follow_list" in follows.keys(): #如果订阅者也订阅了，即拥有follow_list

                        for item in follows["follow_list"]:

                            try:

                                dbcurr.execute('INSERT INTO user(userid, username, files, status, downloaded, lastaccess) VALUES(%s, "%s", 0, 0, 0, %s)' % (item['follow_uk'], item['follow_uname'], str(tnow)))

                                #存储订阅这的用户编号，用户名，入库时间

                            except Exception as ex:

                                print "E13", str(ex)

                                pass

                    else:

                        print "delete 1", uid, start

                        dbcurr.execute('delete from urlids where uk=%s and type=1 and start>%s' % (uid, start))

                elif 'getfanslist' in effective_url: #type = 2,也就是粉丝列表

                    fans = json.loads(metadata)

                    uid = re_uid.findall(effective_url)[0]

                    if "total_count" in fans.keys() and fans["total_count"]>0 and str(start) == "0":

                        for i in range((fans["total_count"]-1)/ONEPAGE):

                            try:

                                dbcurr.execute('INSERT INTO urlids(uk, start, limited, type, status) VALUES(%s, %s, %s, 2, 0)' % (uid, str(ONEPAGE*(i+1)), str(ONEPAGE)))

                            except Exception as ex:

                                print "E2", str(ex)

                                pass



                    if "fans_list" in fans.keys():

                        for item in fans["fans_list"]:

                            try:

                                dbcurr.execute('INSERT INTO user(userid, username, files, status, downloaded, lastaccess) VALUES(%s, "%s", 0, 0, 0, %s)' % (item['fans_uk'], item['fans_uname'], str(tnow)))

                            except Exception as ex:

                                print "E23", str(ex)

                                pass

                    else:

                        print "delete 2", uid, start

                        dbcurr.execute('delete from urlids where uk=%s and type=2 and start>%s' % (uid, start))

                else: #type=0，也即是分享列表

                    shares = json.loads(metadata)

                    uid = re_uid.findall(effective_url)[0]

                    if "total_count" in shares.keys() and shares["total_count"]>0 and str(start) == "0":

                        for i in range((shares["total_count"]-1)/ONESHAREPAGE):

                            try:

                                dbcurr.execute('INSERT INTO urlids(uk, start, limited, type, status) VALUES(%s, %s, %s, 0, 0)' % (uid, str(ONESHAREPAGE*(i+1)), str(ONESHAREPAGE)))

                            except Exception as ex:

                                print "E3", str(ex)

                                pass

                    if "records" in shares.keys():

                        for item in shares["records"]:

                            try:

                                dbcurr.execute('INSERT INTO share(userid, filename, shareid, status) VALUES(%s, "%s", %s, 0)' % (uid, item['title'], item['shareid'])) #item['title']恰好是文件名称

                                #返回的json信息：

                            except Exception as ex:

                                #print "E33", str(ex), item

                                pass

                    else:

                        print "delete 0", uid, start

                        dbcurr.execute('delete from urlids where uk=%s and type=0 and start>%s' % (uid, str(start)))

                dbcurr.execute('delete from urlids where id=%s' % (id, ))

                dbconn.commit()

        except Exception as ex:

            print "E5", str(ex), id

    dbcurr.close()

    dbconn.close() #关闭数据库



def worker():

    global success, failed

    dbconn = mdb.connect(DB_HOST, DB_USER, DB_PASS, 'baiduyun', charset='utf8')

    dbcurr = dbconn.cursor()

    dbcurr.execute('SET NAMES utf8')

    dbcurr.execute('set global wait_timeout=60000')

    #以上是数据库相关设置

    while True:



        #dbcurr.execute('select * from urlids where status=0 order by type limit 1')

        dbcurr.execute('select * from urlids where status=0 and type>0 limit 1') #type>0,为非分享列表

        d = dbcurr.fetchall()

        #每次取出一条数据出来

        #print d

        if d: #如果数据存在

            id = d[0][0] #请求url编号

            uk = d[0][1] #用户编号

            start = d[0][2]

            limit = d[0][3]

            type = d[0][4] #哪种类型

            dbcurr.execute('update urlids set status=1 where id=%s' % (str(id),)) #状态更新为1，已经访问过了

            url = ""

            if type == 0: #分享

                url = URL_SHARE.format(uk=uk, start=start, id=id).encode('utf-8') #分享列表格式化

                #query_uk uk 查询编号

                #start

                #urlid id url编号

            elif  type == 1: #订阅

                url = URL_FOLLOW.format(uk=uk, start=start, id=id).encode('utf-8') #订阅列表格式化

            elif type == 2: #粉丝

                url = URL_FANS.format(uk=uk, start=start, id=id).encode('utf-8') #关注列表格式化

            if url:

                hc_q.put((type, url)) #如果url存在，则放入请求队列，type表示从哪里获得数据

                #通过以上的url就可以获得相应情况下的数据的json数据格式，如分享信息的，订阅信息的，粉丝信息的



            #print "processed", url

        else: #否则从订阅者或者粉丝的引出人中获得信息来存储，这个过程是爬虫树的下一层扩展

            dbcurr.execute('select * from user where status=0 limit 1000')

            d = dbcurr.fetchall()

            if d:

                for item in d:

                    try:

                        dbcurr.execute('insert into urlids(uk, start, limited, type, status) values("%s", 0, %s, 0, 0)' % (item[1], str(ONESHAREPAGE)))

                        #uk 查询号，其实是用户编号

                        #start 从第1条数据出发获取信息

                        #

                        dbcurr.execute('insert into urlids(uk, start, limited, type, status) values("%s", 0, %s, 1, 0)' % (item[1], str(ONEPAGE)))

                        dbcurr.execute('insert into urlids(uk, start, limited, type, status) values("%s", 0, %s, 2, 0)' % (item[1], str(ONEPAGE)))

                        dbcurr.execute('update user set status=1 where userid=%s' % (item[1],)) #做个标志，该条数据已经访问过了

                        #跟新了分享，订阅，粉丝三部分数据

                    except Exception as ex:

                        print "E6", str(ex)

            else:

                time.sleep(1)



        dbconn.commit()

    dbcurr.close()

    dbconn.close()



def main():

    print 'starting at:',now()

    for item in range(16):

        t = threading.Thread(target = req_worker, args = (item,))

        t.setDaemon(True)

        t.start() #请求线程开启，共开启16个线程

    s = threading.Thread(target = worker, args = ())

    s.setDaemon(True)

    s.start() #worker线程开启

    response_worker()  #response_worker开始工作

    print 'all Done at:', now()
