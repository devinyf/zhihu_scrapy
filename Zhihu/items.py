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


from .settings import SQL_DATE_FORMAT
from .utils.common import extract_num

# from .settings import SQL_DATETIME_FORMAT
# from .utils.common import extract_num


def return_value(value):
    # '''直接返回值'''
    return value


def handle_empty(value):
    if not value:
        value = ' '
    return value


def handle_zero(value):
    if not value:
        value = 0
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
    value = ','.join(value)
    match_re = re.match(r".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums


def date_convert(value):
    # '''日期由 str 转换为 date 格式'''
    try:
        date = datetime.datetime.strptime(value, '%Y/%m/%d').date()
    except Exception as e:
        date = datetime.datetime.now().date()

    return date


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


class ZhihuItemLoader(ItemLoader):
    # default_input_processor = MapCompose(rm_mess)
    default_output_processor = TakeFirst()
    # default_output_processor = Join(',')


class ZhihuQuestionItem(scrapy.Item):
    # zhihu 问题 item:
    zhihu_id = scrapy.Field(
        input_processor=get_nums,
    )
    topics = scrapy.Field(
        output_processor=Join(',')
    )
    url = scrapy.Field(
        input_processor=return_value,
    )
    title = scrapy.Field(
        output_processor=Join(',')
    )
    content = scrapy.Field(
        input_processor=handle_empty,
        output_processor=Join(',')
    )
    answer_num = scrapy.Field(
        input_processor=MapCompose(get_nums, handle_zero)
    )
    comments_num = scrapy.Field(
        input_processor=MapCompose(get_nums, handle_zero)
    )
    watch_user_num = scrapy.Field(
        input_processor=MapCompose(get_nums, handle_zero)
    )
    click_num = scrapy.Field(
        input_processor=MapCompose(get_nums, handle_zero)
    )
    # update_time = scrapy.Field()
    # create_time = scrapy.Field()
    # crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into zhihu_question(zhihu_id, topics, url, title,
            content, answer_num, comments_num, watch_user_num, click_num, crawl_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE content=VALUES(content), answer_num=VALUES(answer_num),
            comments_num=VALUES(comments_num),
            watch_user_num=VALUES(watch_user_num), click_num=VALUES(click_num)
        """

        crawl_time = datetime.datetime.now().strftime(SQL_DATE_FORMAT)
        # print(crawl_time)

        params = (self['zhihu_id'], self['topics'], self['url'], self['title'], self['content'],
                  self['answer_num'], self['comments_num'], self['watch_user_num'], self['click_num'], crawl_time)
        print(params)
        return insert_sql, params


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
    # crawl_update_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into zhihu_answer(zhihu_id, url, question_id, author_id, content, praise_num, comments_num, create_time, update_time, crawl_time)
            VALUE (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE content=VALUES(content), comments_num=VALUES(comments_num), praise_num=VALUES(praise_num), update_time=VALUES(update_time)
        """
        create_time = datetime.datetime.fromtimestamp(
            self['create_time']).strftime(SQL_DATE_FORMAT)
        update_time = datetime.datetime.fromtimestamp(
            self['update_time']).strftime(SQL_DATE_FORMAT)
        crawl_time = datetime.datetime.now().strftime(SQL_DATE_FORMAT)
        params = (self['zhihu_id'], self['url'], self['question_id'], self['author_id'], self['content'],
                  self['parse_num'], self['comments_num'], create_time, update_time, crawl_time)

        print(params)
        return insert_sql, params
