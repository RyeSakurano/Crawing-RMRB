# coding=utf-8
'''
crawl.py：爬虫实现和数据的存储
'''

import requests
from bs4 import BeautifulSoup as BS
from functools import reduce
import operator
import datetime
import time
import os


# 发起http请求
def GetHTML(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'
    }
    try:
        r = requests.get(url, headers)
        r.raise_for_status()
        r.encoding = 'utf-8'
        return r.text
    except:
        return ""


# 从当日第一页的网页中统计总页数和所有“要闻”页的链接
def GetPages(year, month, day):
    url = 'http://paper.people.com.cn/rmrb/html/{}-{}/{}/nbs.D110000renmrb_01.htm'.format(
        year, month, day)
    html = GetHTML(url)
    soup = BS(html, 'html.parser')

    tempList = soup.find('div', attrs = {'id': 'pageList'}).ul.find_all(
        'div', attrs = {'class': 'right_title-name'})
    pageCnt = 0
    impLink = []

    for item in tempList:
        link = item.a['href']
        pageCnt += 1 # 总页数
        item = str(item) # 要转为字符串，否则字符串查找会出错
        # 要闻页链接
        if '要闻' in item:
            impLink.append('http://paper.people.com.cn/rmrb/html/{}-{}/{}/{}'.format(year, month, day, link))

    return impLink, pageCnt


# 访问某文章链接，获得其标题（含大小标题）
def GetTitle(url):
    html = GetHTML(url)
    soup = BS(html, 'html.parser')
    return ' '.join([soup.h3.text, soup.h1.text, soup.h2.text])


# 获得某页的文章标题
def GetTitleList(url):
    html = GetHTML(url)
    soup = BS(html, 'html.parser')

    # 找到每一篇文章的链接，访问该页并获得文章标题
    tempList= soup.find('div', attrs = {'id': 'titleList'}).ul.find_all('li')
    titleList = []

    for item in tempList:
        link = item.a['href']
        if 'nw.D110000renmrb' in link:
            url = 'http://paper.people.com.cn/rmrb/html/{}-{}/{}/{}'.format(year, month, day, link)
            titleList.append(GetTitle(url))
            time.sleep(1)
    print(titleList)

    return titleList


# 爬取指定某天的内容
def Process(year, month, day):
    # 获得“要闻”页的链接列表和总页数
    impLink, pageCnt = GetPages(year, month, day)

    # 获得每一个“要闻”页的标题
    titleList = []

    for link in impLink:
        print(link)
        titleList.append(GetTitleList(link))
        time.sleep(3)
    # 头版的文章数
    fpCnt = len(titleList[0])
    # 二维列表变为一维
    titleList = reduce(operator.add, titleList)

    # 将标题列表、统计数据（总页数、“要闻”页数、头版文章数）写入文件
    path = './file/{}{}/'.format(year, month)
    filename = '{}.txt'.format(day)
    if not os.path.exists(path):
        os.makedirs(path)
    with open(path + filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(titleList))
    with open(path + 'stats.txt', 'a', encoding='utf-8') as f:
        f.write(' '.join(map(str, [pageCnt, len(impLink), fpCnt]))+'\n')
   

# 获得开始与结束日期之间（闭区间）的所有日期列表
def GetDateList(startDate, endDate):
    start = datetime.datetime.strptime(startDate, '%Y%m%d')
    end = datetime.datetime.strptime(endDate, '%Y%m%d')
    dates = [start]
    while start < end:
        start += datetime.timedelta(days=1)
        dates.append(start)
    return dates


if __name__ == "__main__":
    startDate = input()
    endDate = input()
    dates = GetDateList(startDate, endDate)

    # 对列表中的每一天进行处理
    for d in dates:
        year = str(d.year)
        month = '{:0>2d}'.format(d.month)
        day = '{:0>2d}'.format(d.day)
        print('Getting {}{}{}'.format(year, month, day))
        Process(year, month, day)
        time.sleep(5)



