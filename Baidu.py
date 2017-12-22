# python 3
# -*- coding: utf-8 -*-
# w_j1ahu1@163.com
# 新工科爬虫

import re
import requests
import time
import pymongo
from config import *

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"}

baidu_json = []


def keyword_search():
    count = 0
    for i in range(0, 20):  # 循环20页爬取结果
        page = (i - 1) * 10
        search_url = 'https://www.baidu.com/s?wd=%E6%96%B0%E5%B7%A5%E7%A7%91&pn=' + str(
            page) + '&oq=%E6%96%B0%E5%B7%A5%E7%A7%91&ie=utf-8&usm=2&rsv_pq=f654e3130000580f&rsv_t=1ff9oxjZN5CfRhCLVjQerO73xSM70PAWKmP5ersn%2BPWX0a75RTdIb3qd%2Fpo'
        try:
            res = requests.get(search_url, headers=headers)
            # print(res.content.decode('utf-8'))
            content_list = re.findall('<h3(.*?)</h3>', res.content.decode('utf-8'), re.S)  # 网页<h3>标签内容（查询结果所在标签）
            # print(content_list)
            # content=content_list[0]
            for content in content_list:
                time.sleep(0.1)
                url_list = 'http:' + str((re.findall('http:(.*?)\"', content, re.S))[0])  # 查询结果的链接
                # print(url_list)
                title_list = str(re.findall('target=\"_blank.*?>(.*?)</a>', content, re.S)[0]).replace('<em>',
                                                                                                       '').replace(
                    '</em>', '')  # 查询结果标题
                # print(title_list)
                try:
                    result_page = requests.get(url_list, headers=headers).content
                except:
                    result_page=''
                time.sleep(0.1)
                # 获得查询结果内容
                try:
                    text_content_t = re.findall(u"[\u4e00-\u9fa5]+", result_page.decode('utf-8'))
                except:
                    text_content_t = ''
                text_content = ''.join(text_content_t)
                # print(text_content)
                baidu_dict = {'title': title_list,
                              'href': url_list,
                              'text_content': text_content,
                              'source': 'baidu',
                              'tf':0}  # 使用字典存储查询结果
                # print(baidu_dict)
                baidu_json.append(baidu_dict)  # 字典转换成json格式
                count = count + 1
                print(count)  # 爬取成功测试计数
        except:
            pass


'''def write():  # 写入文件
    with open('baidu.json', 'w', ) as f:
        json.dump(baidu_json, f)
        print(u'写入文件成功！')
        f.close()'''


def store():# 存储到Mongodb
    for j in baidu_json:
        json = []
        json.append(j)
        if  db[MONGO_TABLE].find({'href':j['href']},{'source':'baidu'}):
            db[MONGO_TABLE].insert(json)
            # print(u'存储成功！')
    print(u'存储成功！')


if __name__ == '__main__':
    keyword_search()
    # write()
    store()
