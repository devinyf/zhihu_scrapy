import sys
sys.path.append('/Users/squall/Documents/WebCrawler/Scrapy_Project/Zhihu/zhihu')

from zheye import zheye

import requests
import shutil
import time
import re
import json

z = zheye()

header = {
    'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
    'Accept-Encoding': 'gzip, deflate',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240'
}

session = requests.session()
response = session.get('http://www.zhihu.com/', headers=header)

match_obj = re.search(r'.*name="_xsrf" value="(.*?)"', response.text)

xsrf = ''
if match_obj:
    xsrf = (match_obj.group(1))
randomNum = str(int(time.time() * 1000))

r = session.get('https://www.zhihu.com/captcha.gif?r={}&type=login&lang=cn'.format(randomNum), headers=header, stream=True)

if r.status_code == 200:
    with open('pic_captcha.gif', 'wb') as f:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)

    positions = z.Recognize('pic_captcha.gif')
    print(positions)

captcha = {}
captcha['input_points'] = []
tmp = []
for poss in positions:
    tmp.append(float(format(poss[0] / 2, '0.2f')))
    tmp.append(float(format(poss[1] / 2, '0.2f')))
    captcha['input_points'].append(tmp)
    tmp = []

# print str(captcha)
params = {
    'phone_num': '18576486260',
    'password': 'ft11253975',
    '_xsrf': xsrf,
    'captcha_type': 'cn',
    #          {"img_size":[200,44],"input_points":[[20.7969,25],[138.797,28]]}
    'captcha': '{"img_size": [200, 44], "input_points": [[%.2f, %f], [%.2f, %f]]}' % (
        positions[0][1] / 2, positions[0][0] / 2, positions[1][1] / 2, positions[1][0] / 2),
}

print(params)
r = session.post('https://www.zhihu.com/login/phone_num', headers=header, params=params)
re_text = json.loads(r.text)
print(re_text)