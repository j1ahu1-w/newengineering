# python 3
# -*- coding:utf-8 -*-
# w_j1ahu1@163.com

import re
import requests
import time
import pymongo
from config import *

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"}
moe_json = []


def keyword_search():
    count = 0
    search_url = 'http://www.moe.gov.cn/was5/web/search?searchword=%E6%96%B0%E5%B7%A5%E7%A7%91&btn_search=&channelid=255182&timescope=&timescopecolumn=&orderby=-DOCRELTIME&perpage=20&searchscope='
    try:
        res = requests.get(search_url, headers=headers).content.decode('utf-8')
        # print(res)
        content_list = re.findall('<h2>(.*?)</h2>', res, re.S)
        # print(content_list)
        for content in content_list:
            url_list = (re.findall('<a href=\'(.*?)\'', content, re.S))[0]
            # print(url_list)
            result_page = requests.get(url_list, headers=headers).content
            title_list = str(re.findall('<h1>(.*?)</h1>', result_page.decode('utf-8'))[0]).replace('<br>','')
            # print(title_list)
            time.sleep(0.)
            # 获得查询结果内容
            try:
                text_content_t = re.findall(u"[\u4e00-\u9fa5]+", result_page.decode('utf-8'))
            except:
                text_content_t = ''
            text_content = ''.join(text_content_t)
            # print(text_content)
            moe_dict = {'title': title_list,
                        'href': url_list,
                        'text_content': text_content,
                        'source': 'moe',
                        'tf':0}  # 使用字典存储查询结果
            # print(moe_dict)
            moe_json.append(moe_dict)  # 字典转换成json格式
            count = count + 1
            print(count)  # 爬取成功测试计数

    except:
        pass


'''def write():  # 写入文件
    with open('moe.json', 'w', ) as f:
        json.dump(moe_json, f)
        print(u'写入文件成功！')
        f.close()'''


def store():# 存储到Mongodb
    for j in moe_json:
        json = []
        json.append(j)
        if db[MONGO_TABLE].find({'href':j['href']},{'source':'moe'}):
            db[MONGO_TABLE].insert(json)
    print(u'存储成功！')


if __name__ == '__main__':
    keyword_search()
    # write()
    store()
