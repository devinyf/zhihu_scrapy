# 直接在项目文件夹下创建main文件,添加如下代码
from scrapy.cmdline import execute
import sys, os

# os.path.dirname 文件夹路径（父文件路径）
# os.path.abspath(__file__) 当前文件路径
# print(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

execute(['scrapy', 'crawl', 'zhihu'])
# execute(['scrapy', 'crawl', 'zhihu1'])