# -*- coding: utf-8 -*-
import scrapy
import re
import json
import requests
import time
import shutil
import sys
import datetime
try:
    import cookielib
except:
    import http.cookiejar as cookielib
try:  # py3
    from urllib import parse
except:  # py2
    import urlparse as parse
from Zhihu.items import ZhihuItemLoader, ZhihuQuestionItem, ZhihuAnswerItem
from w3lib.html import remove_tags

sys.path.append(
    '/Users/squall/Documents/WebCrawler/Scrapy_Project/Zhihu/zhihu')
from zheye import zheye

# from PLI import Image


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/']

    # start_answer_url = 'https://www.zhihu.com/api/v4/questions/{0}/answers?limit=20&offset=0'
    start_answer_url = 'https://www.zhihu.com/api/v4/questions/{}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit=20&offset=43&sort_by=default%20HTTP/1.1'

    headers = {
        'HOST': 'www.zhihu.com',
        'Referer': 'https://www.zhihu.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
    }

    z = zheye()
    session = requests.session()
    # session.cookies = cookielib.LWPCookieJar(filename='cookies.txt')

    def parse(self, response):
        """
        提取出html页面中的所有url 并跟踪这些url进行进一步爬取
        如果提取的url 格式为 ／question/xxx 就下载后直接进入解析函数
        """
        # print(response)

        # 全站搜索过滤法
        all_urls = response.css('a::attr(href)').extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x:True if x.startswith("http") else False, all_urls)
        for url in all_urls:
            match_obj = re.match(r'(.*zhihu.com/question/(\d+?))(/|$)', url)
            if match_obj:
                # 如果提取到 question 相关的页面则下载后交由提取函数处理
                question_url = match_obj.group(1)
                question_id = match_obj.group(2)
                yield scrapy.Request(question_url, meta={'question_id': question_id}, headers=self.headers, callback=self.parse_question)
            else:
                # 如果不是 question 页面则直接进一步跟踪
                yield scrapy.Request(url, headers=self.headers, callback=self.parse)

        # # css 提取法
        # question_list = response.css(
        #     '.AnswerItem .ContentItem-title a::attr(href)').extract()
        # # 组合成绝对路径
        # question_list = [parse.urljoin(response.url, url)
        #                  for url in question_list]
        # print(question_list)
        # for url in question_list:
        #     match_obj = re.match(r'(.*zhihu.com/question/(\d+?))(/|$)', url)
        #     # print(match_obj.group(1))
        #     if match_obj:
        #         question_url = match_obj.group(1)
        #         question_id = match_obj.group(2)
        #         yield scrapy.Request(question_url, meta={'question_id': question_id}, headers=self.headers, callback=self.parse_question)
        #     else:
        #         print('匹配 question 失败')

    def parse_question(self, response):
        # 处理 question 页面， 从页面中提取出具体的 question item
        # if "QuestionHeader-title" in response.text:
        # 处理新版本知乎
        # 回答的api: https://www.zhihu.com/api/v4/questions/263413074/answers?limit=20&offset=23
        question_id = response.meta['question_id']
        print(response.url)
        print(question_id)
        # with open('zhihu_question.html', 'wb') as f:
        #     f.write(response.body)

        item_loader = ZhihuItemLoader(
            item=ZhihuQuestionItem(), response=response)

        item_loader.add_value('zhihu_id', question_id)
        item_loader.add_css('topics', '.TopicLink .Popover div::text')
        item_loader.add_value('url', response.url)
        item_loader.add_css('title', '.QuestionHeader-title::text')
        item_loader.add_css(
            'content', '.QuestionRichText--expandable .RichText::text')
        item_loader.add_css('answer_num', '.List-headerText span::text')
        item_loader.add_css(
            'comments_num', '.QuestionHeader-Comment button::text')
        item_loader.add_css(
            'watch_user_num', '.NumberBoard .NumberBoard-item:nth-child(1) .NumberBoard-value::text')
        item_loader.add_css(
            'click_num', '.NumberBoard .NumberBoard-item:nth-child(3) .NumberBoard-value::text')
        # item_loader.add_css('update_time','')
        # item_loader.add_css('create_time','')

        question_item = item_loader.load_item()
        # print(question_item)
        yield scrapy.Request(self.start_answer_url.format(question_id), headers=self.headers, callback=self.parse_answer)
        yield question_item

    def parse_answer(self, response):
        ans_json = json.loads(response.text)
        is_end = ans_json['paging']['is_end']
        next_url = ans_json['paging']['next']

        for answer in ans_json['data']:
            answer_item = ZhihuAnswerItem()

            answer_item['zhihu_id'] = answer['id']
            answer_item['url'] = answer['url']
            answer_item['question_id'] = answer['question']['id']
            answer_item['author_id'] = answer['author']['id'] if "id" in answer['author'] else None
            answer_item['content'] = remove_tags(answer['content']) if "content" in answer else None
            answer_item['parse_num'] = answer['voteup_count']
            answer_item['comments_num'] = answer['comment_count']
            answer_item['create_time'] = answer['created_time']
            answer_item['update_time'] = answer['updated_time']

            # print(answer_item)
            yield answer_item

        if not is_end:
            yield scrapy.Request(next_url, headers=self.headers, callback=self.parse_answer)


    def start_requests(self):
        # 当有登陆需求需要重写源码中的 start_request， 不重写此命令并没有指定 callback 会默认调用 parse 函数
        yield scrapy.Request('https://www.zhihu.com/#signin', headers=self.headers, callback=self.login)

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
        captcha_url = 'https://www.zhihu.com/captcha.gif?r={}&type=login&lang=cn'.format(
            randomNum)
        yield scrapy.Request(captcha_url, headers=self.headers, meta={'post_data': post_data}, callback=self.get_captcha_login)

    def get_captcha_login(self, response):
        # 验证 倒立汉字验证码
        print(response.url, response.status)
        post_data = response.meta.get('post_data', '')

        if response.status == 200:
            with open('pic_captcha.gif', 'wb') as f:
                f.write(response.body)
                # response.raw.decode_content = True
                # shutil.copyfileobj(response.raw, f)

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
            url='https://www.zhihu.com/login/phone_num',
            formdata=post_data,
            headers=self.headers,
            callback=self.check_login
            # callback = self.after_login
        )

    def check_login(self, response):
        print(response.text)
        text_json = json.loads(response.text)
        if text_json["msg"] == "登录成功":
            for url in self.start_urls:
                yield scrapy.Request(url, dont_filter=True, headers=self.headers)
        else:
            print('验证码错误')

        # 保存登陆状态
        # with open('zhihu_login_result.html', 'wb') as f:
        #     f.write(response.body)
