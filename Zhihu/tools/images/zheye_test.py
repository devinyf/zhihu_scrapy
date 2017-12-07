import sys
sys.path.append('/Users/squall/Documents/WebCrawler/Scrapy_Project/Zhihu/zhihu')

from zheye import zheye
z = zheye()
positions = z.Recognize('captcha-3.gif')
print(positions)