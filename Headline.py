# python 3
# -*- coding: utf-8 -*-
# w_j1ahu1@163.com

import requests
import json
import re
import time
import pymongo
from config import *

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

headline_json = []


def keyword_search():
    count = 0
    for i in range(0, 7):
        x = (i - 1) * 20
        search_url = 'https://www.toutiao.com/search_content/?offset=' + str(
            x) + '&format=json&keyword=%E6%96%B0%E5%B7%A5%E7%A7%91&autoload=true&count=20&cur_tab=1&from=search_tab'
        try:
            time.sleep(0.1)
            res = requests.get(search_url).text
            data = json.loads(res)

            content_list = data['data']
            for content in content_list:
                if 'article_url' in content:
                    url = content['article_url']  # 查询结果链接
                    title = content['title']  # 查询结果标题
                    # print(url)
                    # print(title)
                    result_page = requests.get(url).content
                    time.sleep(0.1)
                    try:
                        text_content_t = re.findall(u"[\u4e00-\u9fa5]+", result_page.decode('utf-8'))
                    except:
                        text_content_t = ''
                    text_content = ''.join(text_content_t)
                    # print(text_content)
                    headline_dict = {'title': title,
                                     'href': url,
                                     'text_content': text_content,
                                     'source': 'headline',
                                     'tf':0}  # 使用字典存储查询结果
                    headline_json.append(headline_dict)  # 字典转换成json格式
                    count = count + 1
                    print(count)  # 爬取成功测试计数
        except:
            pass


'''def write():  # 写入文件
    with open('headline.json', 'w', ) as f:
        json.dump(headline_json, f)
        print(u'写入文件成功！')
        f.close()'''


def store():# 存储到Mongodb
    for j in headline_json:
        json = []
        json.append(j)
        if db[MONGO_TABLE].find({'href':j['href']},{'source':'headline'}):
            db[MONGO_TABLE].insert(json)
    print(u'存储成功！')


if __name__ == '__main__':
    keyword_search()
    # write()
    store()
