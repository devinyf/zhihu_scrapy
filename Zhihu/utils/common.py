# common.py 文件

import hashlib
import re


def get_md5(url):
    # 如果传过来的url没有经过编码，则执行encode
    if isinstance(url, str):
        url = url.encode('utf-8')
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


def extract_num(text):
    # 从字符串中提取出数字
    match_re = re.match(r".*?(\d+).*", text)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0

    return nums


if __name__ == '__main__':
    # python2 不需要encode
    print(get_md5('http://dyfsquall.com')).encode('utf-8')
