# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import re
import datetime
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from w3lib.html import remove_tags

from .settings import SQL_DATETIME_FORMAT
from .utils.common import extract_num


def return_value(value):
    # '''直接返回值'''
    return value


def add_words(value):
    # '''添加字符'''
    return value + 'anyWords'


def rm_words(value):
    # '''去除字符'''
    if 'someWords' in value:
        return ''
    else:
        return value


def extract_list(value):
    return value.extract()[0]


def handle_strip(value):
    return value.strip()


def get_nums(value):
    # '''正则 提取数字 保存为 int 格式'''
    match_re = re.match(r".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums


def date_convert(value):
    # '''日期由 str 转换为 date 格式'''
    try:
        create_date = datetime.datetime.strptime(value, '%Y/%m/%d').date()
    except Exception as e:
        create_date = datetime.datetime.now().date()

    return create_date


def handle_jobaddr(value):
    addr_list = value.split("\n")
    addr_list = [item.strip() for item in addr_list if item.strip() != "查看地图"]
    return " ".join(addr_list)


def rm_mess(value):
    if '\xa0' in value:
        value = value.replace('\xa0', '')
    if '\n' in value:
        value = value.replace('\n', '')
    if '/' in value:
        value = value.replace('/', '')

    value = value.strip()

    return value


class ZhihuItemQuestionItem(scrapy.Item):
    # zhihu 问题 item:
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()


class ZhihuAnswerItem(scrapy.Item):
    # zhihu 回答 item
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    parse_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()
    crawl_update_time = scrapy.Field()
