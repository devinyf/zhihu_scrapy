# -*- coding: utf-8 -*-
import scrapy
import re
import json
import requests
import time
import shutil
import sys
try:
    import cookielib
except:
    import http.cookiejar as cookielib
try:
    from urllib import parse
except:
    import urlparse as parse
sys.path.append(
    '/Users/squall/Documents/WebCrawler/Scrapy_Project/Zhihu/zhihu')
from zheye import zheye
# from PLI import Image



class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/']

    headers = {
        'HOST': 'www.zhihu.com',
        'Referer': 'https://www.zhihu.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
    }

    z = zheye()
    session = requests.session()
    session.cookies = cookielib.LWPCookieJar(filename='cookies.txt')


    # def parse(self, response):
    #     print(response)
    #     all_urls = response.css('a::attr(href)').extract()
    #     all_urls = [parse.urljoin(response.url, url) for url in all_urls]
    #     all_urls = filter(lambda x:True if x.startswith("http") else False, all_urls)
    #     for url in all_urls:
    #         match_obj = re.match('', url)
    #         if match_obj:
    #             # 如果提取到 question 相关的页面则下载后交由提取函数处理
    #             request_url = match_obj.group(1)
    #             yield scrapy.Request(request_url, headers=self.headers, callback=self.parse_question)
    #         else:
    #             # 如果不是 question 页面则直接进一步跟踪
    #             yield scrapy.Request(url, headers=self.headers, callback=self.parse)

    # def parse_question(self, response):
    #     # 处理 question 页面， 从页面中提取出具体的 question item
    #     if "QuestionHeader-title" in response.text:
    #         # 处理新版本知乎
    #         match_obj = re.match('', response.url)
    #         if match_obj:
    #             question_id = int(match_obj.group(2))

    #         item_loader=


    def start_requests(self):
        # 如果不设置 callback 会默认调用 parse 函数
        return [scrapy.Request('https://www.zhihu.com/#signin', headers=self.headers, callback=self.login)]

    def get_xsrf(self, session):
        index_url = 'https://www.zhihu.com'
        # 获取登陆时需要用到的_xsrf
        index_page = session.get(index_url, headers=self.headers)
        html = index_page.text
        pattern = r'name="_xsrf" value="(.*?)"'
        # 此处的_xsrf 返回一个list
        _xsrf = re.findall(pattern, html)
        return _xsrf[0]




    def login(self, response):
        response_text = response.text
        match_obj = re.search('.*name="_xsrf" value="(.*?)"/>', response_text)
        xsrf = ''
        if match_obj:
            xsrf = match_obj.group(1)
        if xsrf:
            session = requests.session()
            post_data = {
                # "_xsrf": self.get_xsrf(self.session),
                "_xsrf": self.get_xsrf(session),
                "phone_num": '18576486260',
                "password": 'ft11253975',
                'captcha': '',
                'captcha_type': 'cn',
            }


        # 生成知乎验证码用的时间戳
        randomNum = str(int(time.time() * 1000))
        captcha_url = 'https://www.zhihu.com/captcha.gif?r={}&type=login&lang=cn'.format(randomNum)
        yield scrapy.Request(captcha_url, headers=self.headers, meta={'post_data': post_data}, callback=self.get_captcha_login)

    def get_captcha_login(self, response):
        # 验证 倒立汉字验证码
        # r = self.session.get('https://www.zhihu.com/captcha.gif?r={}&type=login&lang=cn'.format(
        #     self.randomNum), headers=self.headers, stream=True)
        print(response.url, response.status)
        post_data = response.meta.get('post_data', '')
        # r = response.url

        if response.status == 200:
            with open('pic_captcha.gif', 'wb') as f:
                # response.raw.decode_content = True
                # shutil.copyfileobj(response.raw, f)
                f.write(response.body)

            positions = self.z.Recognize('pic_captcha.gif')
            print(positions)

        pos_arr = []
        if len(positions) == 2:
            if positions[0][1] > positions[1][1]:
                pos_arr.append([positions[1][1], int(positions[1][0])])
                pos_arr.append([positions[0][1], int(positions[0][0])])
            else:
                pos_arr.append([positions[0][1], int(positions[0][0])])
                pos_arr.append([positions[1][1], int(positions[1][0])])

            post_data['captcha'] = '{"img_size": [200, 44], "input_points": [[%.2f, %.f], [%.2f, %.f]]}' % (
                pos_arr[0][0] / 2, pos_arr[0][1] / 2, pos_arr[1][0] / 2, pos_arr[1][1] / 2)
            pos_arr = []

        elif len(positions) == 1:
            pos_arr.append([positions[0][1], int(positions[0][0])])

            post_data['captcha'] = '{"img_size": [200, 44], "input_points": [[%.2f, %.f]]}' % (
                pos_arr[0][0] / 2, pos_arr[0][1] / 2)
            pos_arr = []
        print(post_data)

        # FormRequest 提交表单
        yield scrapy.FormRequest(
            url = 'https://www.zhihu.com/login/phone_num',
            formdata = post_data,
            headers = self.headers,
            callback = self.check_login
        )


    def check_login(self, response):
        print(response.text)
        text_json = json.loads(response.text)
        if "msg" in text_json and text_json["msg"] == "登陆成功":
            for url in self.start_urls:
                yield scrapy.Request(url, dont_filter=True, headers=self.headers)

        # 打印登陆状态
        with open('zhihu_login_result.html', 'wb') as f:
            f.write(response.body)

