# coding: utf-8

import requests
# python2 cookielib, python3 http.cookiejar
try:
    import cookielib
except:
    import http.cookiejar as cookielib

import re
import time
from PIL import Image

import shutil
import sys
sys.path.append(
    '/Users/squall/Documents/WebCrawler/Scrapy_Project/Zhihu/zhihu')
from zheye import zheye

z = zheye()
randomNum = str(int(time.time() * 1000))

session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename='cookies.txt')
try:
    session.cookies.load(ignore_discard=True)
except:
    print('cookie 未能加载')

agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
header = {
    'HOST': 'www.zhihu.com',
    'Referer': 'https://www.zhihu.com',
    'User-Agent': agent
}


def is_login():
    # 通过个人中心页面返回状态来判断是否为登陆状态
    inbox_url = 'https://www.zhihu.com/settings/profile'
    response = session.get(inbox_url, headers=header, allow_redirects=False)
    if response.status_code != 200:
        # 没有登陆
        print('未登陆')
        return False
    else:
        # 已经登陆
        print('已登陆')
        return True


def get_xsrf():
    # 获取 xsrf code
    response = session.get('https://www.zhihu.com', headers=header)
    print(response.text)
    match_obj = re.search(r'.*name="_xsrf" value="(.*?)"', response.text)
    # print(match_obj)
    # print(type(match_obj))
    # xsrf = match_obj.group(1)
    # print(xsrf)

    if match_obj:
        print('获取_xsrf成功')
        return(match_obj.group(1))
    else:
        print('获取_xsrf失败')
        return ""


def get_captcha():
    r = session.get('https://www.zhihu.com/captcha.gif?r={}&type=login&lang=cn'.format(
        randomNum), headers=header, stream=True)

    if r.status_code == 200:
        with open('pic_captcha.gif', 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

        positions = z.Recognize('pic_captcha.gif')
        print(positions)

    pos_arr = []
    if len(positions) == 2:
        if positions[0][1] > positions[1][1]:
            pos_arr.append([positions[1][1], positions[1][0]])
            pos_arr.append([positions[0][1], positions[0][0]])
        else:
            pos_arr.append([positions[1][1], positions[1][0]])
            pos_arr.append([positions[0][1], positions[0][0]])
        captcha = '{"img_size": [200, 44], "input_points": [[%.2f, %f], [%.2f, %f]]}' % (
            pos_arr[0][0] / 2, pos_arr[0][1] / 2, pos_arr[1][0] / 2, pos_arr[1][1] / 2)
        pos_arr = []

    elif len(positions) == 1:
        pos_arr.append([positions[0][1], positions[0][0]])
        captcha = '{"img_size": [200, 44], "input_points": [[%.2f, %f]]}' % (
            pos_arr[0][0] / 2, pos_arr[0][1] / 2)
        pos_arr = []
    # if len(positions) == 2:
    #     captcha = '{"img_size": [200, 44], "input_points": [[%.2f, %f], [%.2f, %f]]}' % (
    #         pos_arr[0][0] / 2, pos_arr[0][1] / 2, pos_arr[1][0] / 2, pos_arr[1][1] / 2)
    # elif len(positions) == 1:
    #     captcha = '{"img_size": [200, 44], "input_points": [[%.2f, %f]]}' % (
    #         pos_arr[0][0] / 2, pos_arr[0][1] / 2)
    return captcha


def get_index():
    """保存登陆页面 检验是否登陆成功"""
    response = session.get('http://www.zhihu.com', headers=header)
    with open("index_page.html", "wb") as f:
        f.write(response.text.encode("utf8"))
    print("save ok")


def zhihu_login(account, password):
    # 知乎登陆

    if re.match(r'^1\d{10}', account):
        print('手机号码登陆')
        post_url = 'https://www.zhihu.com/login/phone_num'
        post_data = {
            "_xsrf": get_xsrf(),
            "phone_num": account,
            "password": password,
            'captcha': get_captcha(),
            "captcha_type": 'cn',
        }
    else:
        if "@" in account:
            print("邮箱方式登陆")
            post_url = 'https://www.zhihu.com/login/email'
            post_data = {
                "_xsrf": get_xsrf(),
                "phone_num": account,
                "password": password,
                'captcha': get_captcha(),
                "captcha_type": 'cn',
            }

    response_text = session.post(post_url, data=post_data, headers=header)
    session.cookies.save()
# text:'{\n    "r": 1,\n    "errcode": 1991829,\n    \n    "data": {"captcha":"\\u9a8c\\u8bc1\\u7801\\u4f1a\\u8bdd\\u65e0\\u6548 :(","name":"ERR_VERIFY_CAPTCHA_SESSION_INVALID"},\n    \n    \n    "msg": "\\u9a8c\\u8bc1\\u7801\\u4f1a\\u8bdd\\u65e0\\u6548 :("\n    \n}'


if __name__ == '__main__':
    if is_login():
        print("已登陆")
    else:
        zhihu_login('18576486260', 'ft11253975')
        # get_index()
        time.sleep(2)
        is_login()
