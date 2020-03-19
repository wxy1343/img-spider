from req import *
import re
import time
import os
import sys
from config import *
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as ThreadPool

requests.packages.urllib3.disable_warnings()
sum = 0
count = 0
url_list = []
threads = 100
retry = True
retry_max = 2
retry_num = 0
pool = ThreadPool(threads)
start_time = 0
end_time = 0


def img_download(url):
    global count
    if os.path.exists('img/' + url[-10:]) == True:
        temp_size = os.path.getsize('img/' + url[-10:])
    elif os.path.exists('img/' + (url[:-4] + '.png')[-10:]) == True:
        temp_size = os.path.getsize('img/' + (url[:-4] + '.png')[-10:])
    else:
        temp_size = 0
    headers = {'Range': 'bytes=%d-' % temp_size}
    r = requests.get(url, stream=True, verify=False, headers=headers)
    if (r.status_code == 404):
        url = url[:-4] + '.png'
        r = requests.get(url, stream=True, verify=False, headers=headers)
    with open('img/' + url[-10:], "ab") as f:
        for chunk in r.iter_content(chunk_size=128):
            if chunk:
                temp_size += len(chunk)
                f.write(chunk)
                f.flush()
        count += 1
        done = int(50 * count / sum)
        char = '╱╲'
        sys.stdout.write("\r\033[0;37;42m    %s下载进度：%d%%|%s%s| %d/%d\033[0m" % (
            char[count % 2], 100 * count / sum, '█' * done, ' ' * (50 - done), count, sum))
        sys.stdout.flush()


def init():
    os.system('title img-spider @吾爱破解 wxy1343')
    print('欢迎使用！\n前往数据源：https://wallhaven.cc 下载更多精彩图片！')
    configdir = 'config.ini'
    global threads
    global retry
    global retry_max
    if not os.path.exists(configdir):
        f = open(configdir, 'a')
        f.close()
        cf = Config(configdir, '配置')
        cf.Add('配置', 'threads', str(threads))
        cf.Add('配置', 'retry', str(retry))
        cf.Add('配置', 'retry_max', str(retry_max))
    else:
        cf = Config(configdir)
        threads = cf.GetInt('配置', 'threads')
        retry = cf.GetBool('配置', 'retry')
        retry_max = cf.GetInt('配置', 'retry_max')


def main():
    # https://wallhaven.cc/search?q=搜索关键词&page=页数
    # 获取figure标签的data-wallpaper-id属性值
    # https://w.wallhaven.cc/full/(data-wallpaper-id前两位)/wallhaven-(data-wallpaper-id).jpg
    init()
    global sum
    global pool
    global start_time
    global end_time
    pool = ThreadPool(threads)
    while True:
        搜索关键词 = input('请输入搜索关键词：')
        if 搜索关键词 != '':
            break
        else:
            print('\033[0;37;41m关键词不能为空！\033[0m')
    while True:
        页数 = input('请输入爬取页数：')
        if re.match('[0-9]{1,}', 页数) != None:
            break
        elif 页数 == '':
            页数 = 1
            break
        else:
            print('\033[0;37;41m你的输入非法，请重新输入！\033[0m')
    start_time = time.time()
    for i in range(int(页数)):
        url = 'https://wallhaven.cc/search?q=' + 搜索关键词 + '&page=' + str(i + 1)
        print('正在爬取第%d页...' % (i + 1))
        req = Req()
        response = req.get(url)
        soup = BeautifulSoup(response.text, features='lxml')
        for j in soup.find_all('figure'):
            url = 'https://w.wallhaven.cc/full/' + j['data-wallpaper-id'][:2] + '/wallhaven-' + j[
                'data-wallpaper-id'] + '.jpg'
            url_list.append(url)
        print('第%d页爬取成功' % (i + 1))

    sum = len(url_list)
    if (sum == 0):
        print('\033[0;37;41m没有匹配的结果，换个关键词试试吧！\033[0m')
        main()
    end_time = time.time()
    print('\033[0;37;42m耗时%f秒\033[0m' % (end_time - start_time))
    if not os.path.exists('img'):
        os.mkdir('img')
    print('开始下载')
    start_time = time.time()
    pool.map(img_download, url_list)
    print('\n下载完成')
    end_time = time.time()
    print('\033[0;37;42m耗时%f秒\033[0m' % (end_time - start_time))
    print('感谢您的使用！')
    input('按Enter键退出')


def Retry():
    global retry_num
    global count
    print('第%d次重试' % retry_num)
    try:
        count = 0
        pool.map(img_download, url_list)
    except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError):
        print('\n\033[0;37;41m远程主机强迫关闭了一个现有的连接。\033[0m')
        if (retry_num < retry_max):
            retry_num += 1
            Retry()
        else:
            print('\n下载失败')
            return
    print('\n下载完成')
    end_time = time.time()
    print('\033[0;37;42m耗时%f秒\033[0m' % (end_time - start_time))
    return


if __name__ == '__main__':
    try:
        main()
    except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError):
        print('\n\033[0;37;41m远程主机强迫关闭了一个现有的连接。\033[0m')
        if (retry and (retry_num < retry_max)):
            retry_num += 1
            Retry()
        print('感谢您的使用！')
        input('按Enter键退出')
