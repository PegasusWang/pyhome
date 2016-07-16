#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
http://www.bjguahao.gov.cn/
"""

import _env
import requests
from pprint import pprint
from web_util import parse_curl_str

CONFIRM_STR = """
curl 'http://www.bjguahao.gov.cn/order/confirm.htm' -H 'Cookie: SESSION_COOKIE=3cab1829cea36ddbceb17f7e; JSESSIONID=23672CA0BED9A20467098C5F4B95646F; Hm_lvt_bc7eaca5ef5a22b54dd6ca44a23988fa=1467855129,1468286722,1468372579,1468459884; Hm_lpvt_bc7eaca5ef5a22b54dd6ca44a23988fa=1468459953' -H 'Origin: http://www.bjguahao.gov.cn' -H 'Accept-Encoding: gzip, deflate' -H 'Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4' -H 'User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36' -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' -H 'Accept: application/json, text/javascript, */*; q=0.01' -H 'Referer: http://www.bjguahao.gov.cn/order/confirm/142-200039542-201105758-38174400.htm' -H 'X-Requested-With: XMLHttpRequest' -H 'Connection: keep-alive' --data 'dutySourceId=38174400&hospitalId=142&departmentId=200039542&doctorId=201105758&patientId=217727400&hospitalCardId=081138697714&medicareCardId=&reimbursementType=1&smsVerifyCode=583293&isFirstTime=2&hasPowerHospitalCard=2&cidType=1&childrenBirthday=&childrenGender=2&isAjax=true' --compressed
"""
CONFIRM_URL, _, CONFIRM_DATA = parse_curl_str(CONFIRM_STR)


def get_qrcode():
    CURL_STR = """
    curl 'http://www.bjguahao.gov.cn/quicklogin.htm' -H 'Cookie: JSESSIONID=79657BDB664F5A7BF7F25EAE9AEC069A; SESSION_COOKIE=3cab1829cea36ddbceb17f7e; Hm_lvt_bc7eaca5ef5a22b54dd6ca44a23988fa=1467855129,1468286722,1468372579,1468459884; Hm_lpvt_bc7eaca5ef5a22b54dd6ca44a23988fa=1468459939' -H 'Origin: http://www.bjguahao.gov.cn' -H 'Accept-Encoding: gzip, deflate' -H 'Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4' -H 'User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36' -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' -H 'Accept: application/json, text/javascript, */*; q=0.01' -H 'Referer: http://www.bjguahao.gov.cn/dpt/appoint/142-200039542.htm' -H 'X-Requested-With: XMLHttpRequest' -H 'Connection: keep-alive' --data 'mobileNo=18810564550&password=199419wnnwnn&yzm=&isAjax=true' --compressed
    """
    url, headers_dict, data = parse_curl_str(CURL_STR)
    del headers_dict['Cookie']    # note must delete this Cookie before login
    with requests.Session() as s:
        r = s.post(url, headers=headers_dict, data=data)    # login
        print(r.text)
        r = s.post(url='http://www.bjguahao.gov.cn/v/sendorder.htm')
        print(r.text)
        # r = s.post(url=CONFIRM_URL, data=CONFIRM_DATA)
        # print(r.text)

    S = """
    curl 'http://www.bjguahao.gov.cn/order/confirm.htm' -H 'Cookie: SESSION_COOKIE=3cab1829cea36ddbceb17f7e; JSESSIONID=23672CA0BED9A20467098C5F4B95646F; Hm_lvt_bc7eaca5ef5a22b54dd6ca44a23988fa=1467855129,1468286722,1468372579,1468459884; Hm_lpvt_bc7eaca5ef5a22b54dd6ca44a23988fa=1468459953' -H 'Origin: http://www.bjguahao.gov.cn' -H 'Accept-Encoding: gzip, deflate' -H 'Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4' -H 'User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36' -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' -H 'Accept: application/json, text/javascript, */*; q=0.01' -H 'Referer: http://www.bjguahao.gov.cn/order/confirm/142-200039542-201105758-38174400.htm' -H 'X-Requested-With: XMLHttpRequest' -H 'Connection: keep-alive' --data 'dutySourceId=38174400&hospitalId=142&departmentId=200039542&doctorId=201105758&patientId=217727400&hospitalCardId=081138697714&medicareCardId=&reimbursementType=1&smsVerifyCode=583293&isFirstTime=2&hasPowerHospitalCard=2&cidType=1&childrenBirthday=&childrenGender=2&isAjax=true' --compressed
    """
    url, _, data = parse_curl_str(S)
    headers = r.request.headers
    cookie_str = headers['Cookie']
    smsVerifyCode = raw_input('input smsVerifyCode:\n')
    confirm(cookie_str, smsVerifyCode)


def confirm(Cookie_str, smsVerifyCode):
    S = """
    curl 'http://www.bjguahao.gov.cn/order/confirm.htm' -H 'Cookie: SESSION_COOKIE=3cab1829cea36ddbceb17f7e; JSESSIONID=23672CA0BED9A20467098C5F4B95646F; Hm_lvt_bc7eaca5ef5a22b54dd6ca44a23988fa=1467855129,1468286722,1468372579,1468459884; Hm_lpvt_bc7eaca5ef5a22b54dd6ca44a23988fa=1468459953' -H 'Origin: http://www.bjguahao.gov.cn' -H 'Accept-Encoding: gzip, deflate' -H 'Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4' -H 'User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36' -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' -H 'Accept: application/json, text/javascript, */*; q=0.01' -H 'Referer: http://www.bjguahao.gov.cn/order/confirm/142-200039542-201105758-38174400.htm' -H 'X-Requested-With: XMLHttpRequest' -H 'Connection: keep-alive' --data 'dutySourceId=38174400&hospitalId=142&departmentId=200039542&doctorId=201105758&patientId=217727400&hospitalCardId=081138697714&medicareCardId=&reimbursementType=1&smsVerifyCode=%s&isFirstTime=2&hasPowerHospitalCard=2&cidType=1&childrenBirthday=&childrenGender=2&isAjax=true' --compressed
    """ % smsVerifyCode
    url, headers, data = parse_curl_str(S)
    headers['Cookie']= Cookie_str
    r = requests.post(url, headers=headers, data=data)
    print(r.text)


if __name__ == '__main__':
    get_qrcode()
