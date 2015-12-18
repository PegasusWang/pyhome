#!/usr/bin/env python
# -*- coding:utf-8 -*-

import html2text

def html2markdown(html):
    """html is unicode"""
    if not html:
        return html
    h = html2text.HTML2Text()
    h.ignore_images = True
    h.ignore_links = True
    return h.handle(html)


def test():
    html = unicode(""" <div class="post_content" id="paragraph">
                <p>如果表格里的数据太多，我们希望可以让表格拉长显示，让页面出现横向滚动条</p>
                <div style="width:100%;display:block">
<div style="width:300px;float:left">
<script type="text/javascript"><!--
google_ad_client = "ca-pub-0652501482160045";
/* 300x250 */
google_ad_slot = "5004934126";
google_ad_width = 300;
google_ad_height = 250;
//-->
</script>
<script type="text/javascript"
        src="http://pagead2.googlesyndication.com/pagead/show_ads.js">
</script>
</div>
<div style="width:300px;float:right">
<script type="text/javascript"><!--
google_ad_client = "ca-pub-0652501482160045";
/* 300x250 */
google_ad_slot = "5004934126";
google_ad_width = 300;
google_ad_height = 250;
//-->
</script>
<script type="text/javascript"
        src="http://pagead2.googlesyndication.com/pagead/show_ads.js">
</script>
</div>
    <div style="clear:both"></div>
</div>


                <p></p>
                <p>
                <div class="code_bar">
                 <span class="title"> <img src="/images/ihome/codes/html.png" class="code_img"><a href="/codes/html/">HTML</a></span>
                </div>


                                    自适应宽度：&nbsp



                                    <pre class="brush:html;gutter:false;">
td {
    width: 1px;
    white-space: nowrap; /* 自适应宽度*/
    word-break:  keep-all; /* 避免长单词截断，保持全部 */
}



</pre>



                                    自适应高度&nbsp



                                    <pre class="brush:html;gutter:false;">
table {
      table-layout: fixed;
      width: 100%;
}
  </pre>



                <br />

            </div>
        """)
    print(html2markdown(html))


if __name__ == '__main__':
    test()
