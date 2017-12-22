# python 3
# -*- coding: utf-8 -*-
# w_j1ahu1@163.com

import jieba
import pymongo
from config import *

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

jieba.load_userdict("word_dict.txt")

major_json = []
major_list = [ '物联网工程', '网络与新媒体', '数字媒体技术', '网络工程', '通信工程', '光电信息科学与工程', '生物制药', '新能源材料与器件', '新能源科学与工程',
              '电子信息工程', '环境生态工程', '环境科学与工程', '建筑环境与能源应用工程', '医学信息工程', '自动化', '安全工程', '微电子科学与工程', '轨道交通信号与控制',
              '飞行器制造工程', '计算机科学与技术', '遥感科学与技术', '智能科学与技术', '信息与计算科学', '集成电路设计与集成系统', '电子与计算机工程', '信息管理与信息系统',
              '智能电网信息工程', '海洋资源开发技术', '船舶与海洋工程', '飞行器适航技术', '水声工程', '空间信息与数字技术', '电子信息科学与技术', '飞行器质量与可靠性',
              '电磁场与无线技术', '环保设备工程', '数据科学与大数据技术', '网络空间安全', '飞行器控制与信息工程', '机器人工程', '材料设计科学与工程', '地理空间信息工程']


def rank():
    for i in major_list:
        count = 0
        text_list = db[MONGO_TABLE].find()
        for t in text_list:
            word_list = jieba.lcut(t['text_content'])
            for word in word_list:
                if i == word:
                    count += 1
        major_dict = {'major': i,
                      'count': count}
        major_json.append(major_dict)
    print(major_json)


def store():
    db[MONGO_MAJOR_TABLE].insert(major_json)
    print(u'存储成功！')

def main():
    rank()
    store()


if __name__ == '__main__':
    main()
