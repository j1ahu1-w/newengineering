# python 3
# -*- coding: utf-8 -*-
# w_j1ahu1@163.com

import time
import jieba
import pymongo
from config import *
import sys
from PyQt5.QtWidgets import (QWidget,QPushButton, QMessageBox, QLineEdit,QLabel,
    QTextEdit,QApplication,QDesktopWidget)
from PyQt5.QtGui import QIcon

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]
jieba.load_userdict("word_dict.txt")


def get_tf(keyword_list):# 获取词频并存储
    set_list = db[MONGO_TABLE].find()
    for l in set_list:
        # print(l)
        word_list = jieba.lcut(l['text_content'])
        word_sum = len(word_list)
        if l['source']=='moe':
            weight=1
        else:
            if l['source'] == 'headline':
                weight=0.5
            else:
                if l['source'] == 'weibo':
                    weight=0.5
                else:
                    if l['source'] == 'baidu':
                        weight=0.3
        # 网页包含中文汉字的词组为0是网页被反爬虫机智阻挠，设置此种网页的词频为0.00015
        # 网页包含中文汉字的词组少于300是网页为视频网页，设置此种网页的词频为0.0001
        # 其他情况认为得到正常网页，依据关键词正常计算其词频
        if word_sum != 0 and word_sum > 300:
            count = 0
            for word in word_list:
                if word in keyword_list:
                    count += 1
            tf = count / word_sum
        else:
            if word_sum != 0 and word_sum < 300:
                tf = 0.0001
            else:
                tf = 0.00015
        l['tf'] = tf*weight # 根据不同网页的权重计算最终词频
        # print(l)
        db[MONGO_TABLE].update({'_id': l['_id']}, l)

class GUI(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # 执行时间标签
        self.time=QLabel('',self)
        self.time.move(50,80)
        self.time.resize(200, 20)
        # Search 按钮
        self.searchButton = QPushButton("Search",self)
        self.searchButton.move(600, 30)
        self.searchButton.resize(80,50)
        # Clear 按钮
        self.clearButton = QPushButton("Clear", self)
        self.clearButton.move(700, 30)
        self.clearButton.resize(80, 50)
        # 搜索框
        self.searchBar = QLineEdit(self)
        self.searchBar.move(50, 30)
        self.searchBar.resize(500,50)
        # 搜索结果框
        self.resultEdit=QTextEdit(self)
        self.resultEdit.move(50, 120)
        self.resultEdit.resize(730,350)
        self.resize( 800, 500)
        self.center()
        self.setWindowTitle('NewEngineering')
        self.setWindowIcon(QIcon('icon.jpg'))
        self.show()
        self.searchButton.clicked.connect(self.fun)
        self.clearButton.clicked.connect(self.clear)

    def fun(self):
        start=time.clock()
        keyword_list=jieba.lcut_for_search(self.searchBar.text())
        # print(keyword_list)
        # 检索词中含有专业排名则返回排名
        # 否则正常搜索
        if ('专业' in keyword_list) and ('排名' in keyword_list):
            result=db[MONGO_MAJOR_TABLE].find().sort([('count', -1)])
            count = 1
            for r in result[0:42]:
                if count<=9:
                    t = '0' + str(count) + '  ' + r['major']
                else:
                    t =  str(count) + '  ' + r['major']
                self.resultEdit.append(t)
                count += 1
            end = time.clock()
            ex_time = 'Excute Time:' + str(end - start)
            # print(ex_time)
            self.time.setText(ex_time)
        else:
            # db[MONGO_TABLE].ensure_index([('tf', -1)])
            get_tf(keyword_list)
            result = db[MONGO_TABLE].find().sort([('tf', -1)])
            count = 1
            for r in result[0:30]:
                t = str(count) + '  ' + r['title']
                self.resultEdit.append(t)
                self.resultEdit.append(r['href'])
                count += 1
            end = time.clock()
            ex_time = 'Excute Time:' + str(end - start)
            # print(ex_time)
            self.time.setText(ex_time)

    def clear(self):
        self.searchBar.setText('')
        self.resultEdit.setText('')
        self.time.setText('')

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to exit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GUI()
    sys.exit(app.exec_())
