# 模拟登陆微博源码参考：https://github.com/xchaoinfo/fuck-login
# python 3
# -*- coding: utf-8 -*-
# w_j1ahu1@163.com

import time
import base64
import rsa
import binascii
import requests
import re
import random
import pymongo
from config import *

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]


try:
    from PIL import Image
except:
    pass
try:
    from urllib.parse import quote_plus
except:
    from urllib import quote_plus
'''
如果没有开启登录保护，不用输入验证码就可以登录
如果开启登录保护，需要输入验证码
'''

# 构造 Request headers
agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0'
headers = {
    'User-Agent': agent
}

session = requests.session()

# 访问 初始页面带上 cookie
index_url = "http://weibo.com/login.php"
try:
    session.get(index_url, headers=headers, timeout=2)
except:
    session.get(index_url, headers=headers)
try:
    input = raw_input
except:
    pass


def get_su(username):
    """
    对 email 地址和手机号码 先 javascript 中 encodeURIComponent
    对应 Python 3 中的是 urllib.parse.quote_plus
    然后在 base64 加密后decode
    """
    username_quote = quote_plus(username)
    username_base64 = base64.b64encode(username_quote.encode("utf-8"))
    return username_base64.decode("utf-8")


# 预登陆获得 servertime, nonce, pubkey, rsakv
def get_server_data(su):
    pre_url = "http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su="
    pre_url = pre_url + su + "&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.18)&_="
    pre_url = pre_url + str(int(time.time() * 1000))
    pre_data_res = session.get(pre_url, headers=headers)

    sever_data = eval(pre_data_res.content.decode("utf-8").replace("sinaSSOController.preloginCallBack", ''))

    return sever_data


# print(sever_data)


def get_password(password, servertime, nonce, pubkey):
    rsaPublickey = int(pubkey, 16)
    key = rsa.PublicKey(rsaPublickey, 65537)  # 创建公钥
    message = str(servertime) + '\t' + str(nonce) + '\n' + str(password)  # 拼接明文js加密文件中得到
    message = message.encode("utf-8")
    passwd = rsa.encrypt(message, key)  # 加密
    passwd = binascii.b2a_hex(passwd)  # 将加密信息转换为16进制。
    return passwd


def get_cha(pcid):
    cha_url = "http://login.sina.com.cn/cgi/pin.php?r="
    cha_url = cha_url + str(int(random.random() * 100000000)) + "&s=0&p="
    cha_url = cha_url + pcid
    cha_page = session.get(cha_url, headers=headers)
    with open("cha.jpg", 'wb') as f:
        f.write(cha_page.content)
        f.close()
    try:
        im = Image.open("cha.jpg")
        im.show()
        im.close()
    except:
        print(u"请到当前目录下，找到验证码后输入")


def login(username, password):
    # su 是加密后的用户名
    su = get_su(username)
    sever_data = get_server_data(su)
    servertime = sever_data["servertime"]
    nonce = sever_data['nonce']
    rsakv = sever_data["rsakv"]
    pubkey = sever_data["pubkey"]
    showpin = sever_data["showpin"]
    password_secret = get_password(password, servertime, nonce, pubkey)

    postdata = {
        'entry': 'weibo',
        'gateway': '1',
        'from': '',
        'savestate': '7',
        'useticket': '1',
        'pagerefer': "http://login.sina.com.cn/sso/logout.php?entry=miniblog&r=http%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl",
        'vsnf': '1',
        'su': su,
        'service': 'miniblog',
        'servertime': servertime,
        'nonce': nonce,
        'pwencode': 'rsa2',
        'rsakv': rsakv,
        'sp': password_secret,
        'sr': '1366*768',
        'encoding': 'UTF-8',
        'prelt': '115',
        'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
        'returntype': 'META'
    }
    login_url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'
    if showpin == 0:
        login_page = session.post(login_url, data=postdata, headers=headers)
    else:
        pcid = sever_data["pcid"]
        get_cha(pcid)
        postdata['door'] = input(u"请输入验证码")
        login_page = session.post(login_url, data=postdata, headers=headers)
    login_loop = (login_page.content.decode("GBK"))
    # print(login_loop)
    pa = r'location\.replace\([\'"](.*?)[\'"]\)'
    loop_url = re.findall(pa, login_loop)[0]
    # print(loop_url)
    # 此出还可以加上一个是否登录成功的判断，下次改进的时候写上
    login_index = session.get(loop_url, headers=headers)
    uuid = login_index.text
    uuid_pa = r'"uniqueid":"(.*?)"'
    uuid_res = re.findall(uuid_pa, uuid, re.S)[0]
    web_weibo_url = "http://weibo.com/%s/profile?topnav=1&wvr=6&is_all=1" % uuid_res
    weibo_page = session.get(web_weibo_url, headers=headers)
    weibo_pa = r'<title>(.*?)</title>'
    # print(weibo_page.content.decode("utf-8"))
    userID = re.findall(weibo_pa, weibo_page.content.decode("utf-8", 'ignore'), re.S)[0]
    print(u"模拟登录微博成功")

weibo_json = []

def keyword_search():
    count = 0
    title = []
    url_list = []
    login(username, password)
    for page in range(0, 4):
        search_url = 'http://s.weibo.com/list/relpage?search=%25E6%2596%25B0%25E5%25B7%25A5%25E7%25A7%2591&page=' + str(
            page)
        try:
            res = session.get(search_url, headers=headers)
            content_list = re.findall('<script>.*?\"pl_list_relpage\",(.*?)</script>', res.content.decode('utf-8'),
                                      re.S)
            # print(content_list)
            for content in content_list:
                # print(content)
                url_list_temp = re.findall('W_texta W_fb.*?href=(.*?)title', content, re.S)
                # print(url_list_temp)
                title_list_temp = re.findall('W_texta W_fb.*?title=(.*?)target', content, re.S)
                # print('title_list_temp:',title_list_temp)
                for title_list in title_list_temp:  # 获取文章标题列表
                    t = str(re.findall('\\\\\"(.*?)\\\\\"', title_list, re.S)).replace('[\'', '').replace('\']', '')
                    title.append(t.replace("\\\\u", '\\u').encode('latin-1').decode('unicode_escape'))

                for url in url_list_temp:  # 获取链接列表
                    url_list.append(url.replace("\\", "").replace("\"", ""))
        except:
            pass
    # print(url_list)
    # print(title)
    try:
        for u, ti in zip(url_list, title):  # 联合循环，获得文章内容
            time.sleep(0.2)
            result_page = session.get(u, headers=headers).content
            # print(ti)
            # print(u)
            # 获得文章内容
            try:
                text_content_t = re.findall(u"[\u4e00-\u9fa5]+", result_page.decode('utf-8'))
            except:
                text_content_t = ''
            text_content = ''.join(text_content_t)
            # print(text_content)
            weibo_dict = {'title': ti,
                          'href': u,
                          'text_content': text_content,
                          'source': 'weibo',
                          'tf':0}  # 使用字典存储结果
            weibo_json.append(weibo_dict)  # 字典转换成json格式
            count = count + 1
            print(count)  # 爬取成功测试计数
    except:
        pass


'''def write():  # 写入文件
    with open('weibo.json', 'w', ) as f:
        json.dump(weibo_json, f)
        print(u'写入文件成功！')
        f.close()'''


def store():# 存储到Mongodb
    for j in weibo_json:
        json = []
        json.append(j)
        if db[MONGO_TABLE].find({'href':j['href']},{'source':'weibo'}):
            db[MONGO_TABLE].insert(json)
    print(u'存储成功！')


if __name__ == "__main__":
    username = input(u'用户名：')
    password = input(u'密码：')
    keyword_search()
    # write()
    store()
