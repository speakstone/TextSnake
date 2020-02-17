# -*- coding:utf-8 -*-
import re
import requests


def dowmloadPic(html, keyword, url_i):
    pic_url = re.findall('"objURL":"(.*?)",', html, re.S)
    i = 1
    print('找到关键词:' + keyword + '的图片，现在开始下载图片...')
    for each in pic_url:
        print('正在下载第' + str(i) + '张图片，图片地址:' + str(each))
        try:
            pic = requests.get(each, timeout=5)
        # except requests.exceptions.ConnectionError:
        except:
            print('【错误】当前图片无法下载')
            continue

        dir = 'JPG/' + keyword + "_" + str(url_i) + '_' + str(i) + '.jpg'
        fp = open(dir, 'wb')
        fp.write(pic.content)
        fp.close()
        i += 1


if __name__ == '__main__':
    word = input("Input key word: ")
    for url_i in range(30):
        url = 'http://image.baidu.com/search/flip?tn=baiduimage&ie=utf-8&word=' + word + '&ct=201326592&v=flip&pn=' + str(url_i)
        try:
            result = requests.get(url)
        except:
            print("worry url"+str(url_i))
        dowmloadPic(result.text, word, url_i)
