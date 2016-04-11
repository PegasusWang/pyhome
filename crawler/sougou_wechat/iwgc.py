#!/usr/bin/env python
# -*- coding:utf-8 -*-

import _env
from lib._db import get_collection
from extract import extract, extract_all
from web_util import requests
from config.config import CONFIG

"""
抓取http://www.iwgc.cn/网站微信公众号列表
<a href="/1" id="cat-1" class="list-group-item">创意&middot;科技</a>
<a href="/2" id="cat-2" class="list-group-item">媒体&middot;达人</a>
<a href="/3" id="cat-3" class="list-group-item">摄影&middot;旅行</a>
<a href="/4" id="cat-4" class="list-group-item">生活&middot;家居</a>
<a href="/5" id="cat-5" class="list-group-item">学习&middot;工具</a>
<a href="/6" id="cat-6" class="list-group-item">历史&middot;读书</a>
<a href="/7" id="cat-7" class="list-group-item">金融&middot;理财</a>
<a href="/8" id="cat-8" class="list-group-item">电影&middot;音乐</a>
<a href="/9" id="cat-9" class="list-group-item">美食&middot;菜谱</a>
<a href="/10" id="cat-10" class="list-group-item">外语&middot;教育</a>
<a href="/11" id="cat-11" class="list-group-item">宠物&middot;休闲</a>
<a href="/12" id="cat-12" class="list-group-item">健康&middot;医疗</a>
<a href="/13" id="cat-13" class="list-group-item">时尚&middot;购物</a>
<a href="/14" id="cat-14" class="list-group-item">公司&middot;宣传</a>
<a href="/15" id="cat-15" class="list-group-item">游戏&middot;娱乐</a>

"""

COL = get_collection(CONFIG.MONGO.DATABASE, 'wechat_name')


def wechat_list():
    for _id in range(1, 16):
        url = 'http://www.iwgc.cn/%d' % _id
        page = 1
        res = []

        while True:
            page_url = url + '/p/' + str(page)
            html = requests.get(page_url).text
            detail_list = extract_all('<div class="detail">', '</div>', html)
            name_list = [extract('title="', '"', tag) for tag in detail_list]
            if not name_list:
                break
            else:
                res.extend(name_list)
            page += 1

        COL.update(
            {'_id': _id},
            {
                '$set': {'name_list': res}
            },
            upsert=True
        )


def name_list(_id, name="name_list"):
    l = COL.find_one(_id).get(name)
    return [s.strip() for s in set(l)]


TAG_DICT = {
    1: ['36氪', '创见'],
    2: ['ZAKER'],
    3: ['摄影笔记'],
    4: ['壹心理', 'KnowYourself'],
    5: ['麻省理工科技评论'],
    6: ['青年文摘'],
    7: ['简七理财', '力哥说理财', '格上理财', '和讯理财',
        '华尔街见闻', '互联网金融观察', '哈佛商业评论'],
    8: ['电影天堂'],
    9: ['北京吃货'],
    10: ['英语学习笔记'],
    11: ['全球奇闻轶事'],
    12: ['硬派健身'],
    13: ['男装搭配'],
    14: ['创业邦杂志'],
    15: ['神吐槽'],
    # 技术编程
    16: ['高可用架构', 'Linux爱好者', 'Python开发者', '稀土圈', '伯乐在线',
            '极客范', 'Python程序员', '架构师', '编程派',
            '电脑报', ' InfoQ', '好东西传送门', '机器之心', '并发编程网',
            '开源中国', 'github', 'caoz的梦呓', '前端大全', 'Linux中国'],
    # 创意科技
    17: ['互联网+', '36氪', '创见', '虎嗅网', '科技每日推送', '神秘的程序员们',
            'Zealer中国', '知乎日报', '麻省理工科技评论', '少数派', '商业价值',
            '小道消息', '网易科技', '搜狐科技', '创业家', '创投界'],
    # 金融理财
    18: ['简七理财', '力哥说理财', '格上理财', '和讯理财', '金融八卦女',
        '华尔街见闻', '互联网金融观察', '哈佛商业评论', '跑赢大盘的王者',
            '港股那点事', '21世纪经济报道', '股社区', '天天说钱', '揭幕者',
            '黄生看金融', '吴晓波频道', '钱眼', '央视财经', '基金圈',
            '南方基金微视界', '天天基金网', '天弘基金',],
    # 生活心理
    19: ['视觉志', 'papi', '壹心理', 'KnowYourself', '硬派健身', '丁香医生', '果壳网',
            '商务范', '时尚芭莎', '每天学点穿衣打扮', '咪蒙',
            '海报网', '瑞丽网', '简书', '奇葩说', '微精选', '水木文摘',
            '美丽说', '美美家族'],
    # 电影音乐
    20: ['电影天堂', '全球电影排行榜', '毒舌电影', '耳帝', '独立鱼电影',
            'Mtime时光网', '抠电影', '搜狐娱乐', '豆瓣电影'],
    # 段子节操
    21 :['冷丫', '冷兔', '内涵段子', '煎蛋', '我们爱讲冷笑话', '卡娃微卡',
            '同道大叔', '冷笑话精选', '冷笑话', '小贱鸡', '马桶阅读',
            '任真天', '我们爱讲冷笑话', '新闻哥', '大爱猫咪控', '好狗狗'],
}


def tagid_by_name(name):
    for tag_id, name_list in TAG_DICT.items():
        if name in name_list:
            return int(tag_id)
    return None


def set_need_name_list(_id):
    """手工设置需要爬的帐号，选取高质量内容"""
    COL.update(
        {'_id': _id},
        {
            '$set': {'need_name_list': TAG_DICT[_id]}
        },
        upsert=True
    )


if __name__ == '__main__':
    for _id in range(16, 22):
        set_need_name_list(_id)

