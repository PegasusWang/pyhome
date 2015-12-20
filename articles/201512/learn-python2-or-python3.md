最近笔者在知乎上看到一个问题[应该学习最新版本的 Python 3 还是旧版本的 Python 2？](https://www.zhihu.com/question/24549965)，笔者当年是学习的python2.7入门的，国内关于python3的中文资料很少，最近工作技术老大比较激进，直接用的python3.5，顺便也了解了一下python3.5的一些新特性。究竟该学python2还是python3呢？笔者认为应该学最新的python3。python3做了不少改进，社区果断舍弃了python2中不好的特性，同时增加了一些非常方便好用的特性和新功能(Asyncio库等)，也改进了旧库中一些不够好的设计(urllib等)，如果没有历史包袱，就直接学习最新的python3。当然很多批评人士认为python3做了这么大改进，不兼容旧代码，略坑爹。不过笔者认为这种做法还是很好的，免得像某些语言（c艹）等不断兼容，搞得越来越复杂。

___
目前社区也提供了2to3工具来进行python2到3代码的转化，并且很多库也都兼容python3了，（著名的爬虫框架scrapy还不支持），很多不再维护的库可能也不支持了。不过如果衡量下项目使用的库都支持python3了，就可以果断迁移了。对于没有历史包袱的初学者，也可以直接学习python3。参考资料有一些python3的介绍和《div into python3》这本书的html版，笔者还会在本网站【资源】这一栏继续分享python3的学习资料。

___
####参考
[python3新特性介绍](https://asmeurer.github.io/python3-presentation/slides.html#1)

[Porting Code to Python 3 with 2to3
](http://www.diveintopython3.net/porting-code-to-python-3-with-2to3.html)