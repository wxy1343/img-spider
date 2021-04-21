from req import *
import random
import re
import time
import os
import sys
from config import *
from bs4 import BeautifulSoup
from threading import Lock
from multiprocessing.dummy import Pool as ThreadPool

requests.packages.urllib3.disable_warnings()
sum = 0
count = 0
url_list = []
url_lists = []
favorites_url_list = []
favorites_index = 0
thread = True
threads_num = 100
retry = True
retry_max = 999999999
retry_num = 0
output = False
error_info = True
pool = ThreadPool(threads_num)
start_time = 0
end_time = 0
time_out_retry_num = 0
time_out = 10
lock = Lock()


def img_download(args):
    global time_out_retry_num
    global retry_num
    name, url = args
    if name != '':
        path = 'img/' + name + '/'
    else:
        path = 'img/'
    while True:
        try:
            if os.path.exists(path + url[-10:]) == True:
                temp_size = os.path.getsize(path + url[-10:])
            elif os.path.exists(path + (url[:-4] + '.png')[-10:]) == True:
                temp_size = os.path.getsize(path + (url[:-4] + '.png')[-10:])
            else:
                temp_size = 0
            headers = {'Range': 'bytes=%d-' % temp_size}
            r = requests.get(url, stream=True, verify=False, headers=headers, timeout=time_out)
            while r.status_code == 503:
                r = requests.get(url, stream=True, verify=False, headers=headers, timeout=time_out)
            if (r.status_code == 404):
                url = url[:-4] + '.png'
                r = requests.get(url, stream=True, verify=False, headers=headers, timeout=time_out)
                while r.status_code == 503:
                    r = requests.get(url, stream=True, verify=False, headers=headers, timeout=time_out)
            with open(path + url[-10:], "ab") as f:
                for chunk in r.iter_content(chunk_size=128):
                    if chunk:
                        temp_size += len(chunk)
                        f.write(chunk)
                        f.flush()
        except requests.exceptions.ReadTimeout:
            time_out_retry_num += 1
            if error_info:
                with lock:
                    print('\n\033[0;37;41m超时重试%d次。\033[0m' % time_out_retry_num)
        except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError):
            if error_info:
                with lock:
                    print('\n\033[0;37;41m远程主机强迫关闭了一个现有的连接。\033[0m')
            if (retry and (retry_num < retry_max)):
                retry_num += 1
                if error_info:
                    with lock:
                        print('第%d次重试' % retry_num)
            else:
                with lock:
                    print('\n下载失败')
                    print('感谢您的使用！')
                    input('按Enter键退出')
                sys.exit()
        else:
            break
    with lock:
        progress_bar('下载进度', sum)


def progress_bar(text, sum):
    global count
    count += 1
    done = int(50 * count / sum)
    char = '╱╲'
    sys.stdout.write("\r\033[0;37;42m    %s%s：%d%%|%s%s| %d/%d\033[0m" % (
        char[count % 2], text, 100 * count / sum, '█' * done, ' ' * (50 - done), count, sum))
    sys.stdout.flush()


def init():
    os.system('title img-spider @吾爱破解 wxy1343')
    print('欢迎使用！\n前往数据源：https://wallhaven.cc 下载更多精彩图片！')
    configdir = 'config.ini'
    global thread
    global threads_num
    global retry
    global retry_max
    global output
    global time_out
    global error_info
    if not os.path.exists(configdir):
        f = open(configdir, 'a')
        f.close()
        cf = Config(configdir, '配置')
        cf.Add('配置', 'thread', str(thread))
        cf.Add('配置', 'threads_num', str(threads_num))
        cf.Add('配置', 'retry', str(retry))
        cf.Add('配置', 'retry_max', str(retry_max))
        cf.Add('配置', 'output', str(output))
        cf.Add('配置', 'time_out', str(time_out))
        cf.Add('配置', 'error_info', str(error_info))
    else:
        cf = Config(configdir, '配置')
        thread = cf.GetBool('配置', 'thread')
        threads_num = cf.GetInt('配置', 'threads_num')
        retry = cf.GetBool('配置', 'retry')
        retry_max = cf.GetInt('配置', 'retry_max')
        output = cf.GetBool('配置', 'output')
        time_out = cf.GetInt('配置', 'time_out')
        error_info = cf.GetBool('配置', 'error_info')
    if not thread:
        threads_num = 1


def parse(url, 开始页数, 页数):
    for i in range(开始页数, 页数):
        urls = url + 'page=' + str(i + 1)
        print('正在爬取第%d页...' % (i + 1))
        req = Req()
        response = req.get(urls)
        soup = BeautifulSoup(response.text, features='lxml')
        for j in soup.find_all('figure'):
            urls = 'https://w.wallhaven.cc/full/' + j['data-wallpaper-id'][:2] + '/wallhaven-' + j[
                'data-wallpaper-id'] + '.jpg'
            if urls not in url_list:
                url_list.append(urls)
        print('第%d页爬取成功' % (i + 1))


def parse_mul(url):
    global retry_num
    global time_out_retry_num
    req = Req()
    while True:
        try:
            response = req.get(url, timeout=time_out)
        except requests.exceptions.ReadTimeout:
            time_out_retry_num += 1
            if error_info:
                with lock:
                    print('\n\033[0;37;41m超时重试%d次。\033[0m' % time_out_retry_num)
        except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError):
            if error_info:
                with lock:
                    print('\n\033[0;37;41m远程主机强迫关闭了一个现有的连接。\033[0m')
            if (retry and (retry_num < retry_max)):
                retry_num += 1
                if error_info:
                    with lock:
                        print('第%d次重试' % retry_num)
            else:
                with lock:
                    print('\n爬取失败')
                    print('感谢您的使用！')
                    input('按Enter键退出')
                sys.exit()
        else:
            if response.status_code != 200:
                parse_mul(url)
                return
            soup = BeautifulSoup(response.text, features='lxml')
            for j in soup.find_all('figure'):
                urls = 'https://w.wallhaven.cc/full/' + j['data-wallpaper-id'][:2] + '/wallhaven-' + j[
                    'data-wallpaper-id'] + '.jpg'
                if urls not in url_list:
                    url_list.append(urls)
            progress_bar('爬取进度', sum)
            break


def parse_favorites(url):
    req = Req()
    response = req.get(url)
    soup = BeautifulSoup(response.text, features='lxml')
    favorites_url_list = []
    for i, j in enumerate(soup.find('ul', id='collections').find_all('li', {'class': 'collection'})):
        name = j.find('span', {'class': 'collection-label'}).text
        print(str(i + 1) + '.' + name)
        url = j.find('a')['href'] + '?'
        favorites_url_list.append((name, url))
    return favorites_url_list


def get_page():
    start_page = 0
    while True:
        page = input('请输入爬取页数：').strip()
        if re.match('^\d+$', page) != None:
            break
        elif page == '':
            page = 1
            break
        elif re.match('^\d+(\s+|,+|-+)\d+$', page) != None:
            if (',' in page):
                start_page = page.split(',')[0]
                page = page.split(',')[-1]
            if (' ' in page):
                start_page = page.split()[0]
                page = page.split()[-1]
            if ('-' in page):
                start_page = page.split('-')[0]
                page = page.split('-')[-1]
            if (int(start_page) > int(page)) or (int(start_page) <= 0):
                print('\033[0;37;41m你的输入非法，请重新输入！\033[0m')
                continue
            break
        else:
            print('\033[0;37;41m你的输入非法，请重新输入！\033[0m')
    if start_page != 0:
        start_page = int(start_page) - 1
    page = int(page)
    return start_page, page


def Retry(f):
    global count
    global retry_num
    while True:
        try:
            f()
        except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError):
            if error_info:
                with lock:
                    print('\n\033[0;37;41m远程主机强迫关闭了一个现有的连接。\033[0m')
            if (retry and (retry_num < retry_max)):
                retry_num += 1
                if error_info:
                    with lock:
                        print('第%d次重试' % retry_num)
                count = 0
            else:
                with lock:
                    print('\n下载失败')
                    print('感谢您的使用！')
                    input('按Enter键退出')
                sys.exit()
        else:
            break


def favorites(name, url):
    global url_list
    global url_lists
    global favorites_url_list
    global favorites_index
    global sum
    global count
    global retry_num
    global time_out_retry_num
    start_page, page = get_page()
    url_lists = []
    for i in range(start_page, page):
        url_lists.append(url + 'page=' + str(i + 1))
    sum = page - start_page
    print('开始爬取...')
    start_time = time.time()
    count = 0
    retry_num = 0
    if thread:
        pool.map(parse_mul, url_lists)
    else:
        parse(url, start_page, page)
    url_lists = [(name, url) for url in url_list]
    sum = len(url_list)
    if (sum == 0):
        print('\033[0;37;41m"%s"为空,正在爬取下一个！\033[0m' % name)
        return
    print('\n爬取完毕')
    if output:
        to_txt(url_list)
        return
    if not os.path.exists('img/' + name + '/'):
        os.mkdir('img/' + name + '/')
    end_time = time.time()
    print('\033[0;37;42m耗时%f秒\033[0m' % (end_time - start_time))
    print('开始下载')
    start_time = time.time()
    count = 0
    retry_num = 0
    time_out_retry_num = 0
    pool.map(img_download, url_lists)
    print('\n下载完成')
    end_time = time.time()
    print('\033[0;37;42m耗时%f秒\033[0m' % (end_time - start_time))


def read_txt(path):
    list = []
    with open(path, 'r') as f:
        for i in f.readlines():
            if i != '':
                list.append(i.strip().replace('\n', ''))
        return list


def to_txt(list):
    txt = ''
    for i in list:
        txt += i + '\n'
    txt = txt[:-1]
    if not os.path.exists('output'):
        os.mkdir('output')
    with open('output\\' + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + '.txt', 'w') as f:
        f.write(txt)


def txt_spider():
    global sum
    global count
    global retry_num
    global time_out_retry_num
    global favorites_url_list
    global url_list
    path = input('请输入文本路径：')
    name = path.split('\\')[-1].split('.')[0]
    l = read_txt(path)
    for url in l:
        url_list=[]
        count=0
        print('正在爬取：' + url)
        if re.match('^(https://|http://|)wallhaven.cc($|/.*\?|/.*$|/)', url) != None:
            if '&page=' in url:
                url = url.split('&page=')[0] + '&'
            elif '?page=' in url:
                url = url.split('?page=')[0] + '?'
            elif re.match('.*favorites($|/$)', url):
                start_time = time.time()
                print('正在爬取收藏中...')
                favorites_url_list = parse_favorites(url.rstrip())
                end_time = time.time()
                print('\033[0;37;42m耗时%f秒\033[0m' % (end_time - start_time))
            elif url.rstrip()[-1] == '/':
                url = url[:-1] + '?'
            else:
                url = url.rstrip() + '?'
            spider(url, name, False)
    with lock:
        print('感谢您的使用！')
        input('按Enter键退出')


def main():
    # https://wallhaven.cc/search?q=搜索关键词&page=页数
    # 获取figure标签的data-wallpaper-id属性值
    # https://w.wallhaven.cc/full/(data-wallpaper-id前两位)/wallhaven-(data-wallpaper-id).jpg
    init()
    global sum
    global pool
    global start_time
    global end_time
    global url_list
    global favorites_url_list
    global favorites_index
    global count
    global retry_num
    global time_out_retry_num
    pool = ThreadPool(threads_num)
    name = ''
    while True:
        print('1.搜索关键词\n2.最新\n3.排行榜\n4.随机\n5.自定义\n6.文本')
        choice = input('请输入序号：')
        if choice == '1':
            while True:
                keyword = input('请输入搜索关键词：').strip()
                if keyword != '':
                    break
                else:
                    print('\033[0;37;41m关键词不能为空！\033[0m')
            url = 'https://wallhaven.cc/search?q=' + keyword + '&'
            name = keyword
            break
        elif choice == '2':
            name = 'latest'
            url = 'https://wallhaven.cc/latest?'
            break
        elif choice == '3':
            name = 'toplist'
            url = 'https://wallhaven.cc/toplist?'
            break
        elif choice == '4':
            seed = input('请输入种子（留空随机种子）：')
            if (seed.strip() == ''):
                seed = ''.join(random.sample([chr(i) for i in range(65, 91)] + [chr(i) for i in range(97, 123)], 5))
                print('你的随机种子是：' + seed)
            name = seed
            url = 'https://wallhaven.cc/random?seed=' + seed + '&'
            break
        elif choice == '5':
            while True:
                with lock:
                    url = input('请输入自定义网址：').strip()
                if re.match('^(https://|http://|)wallhaven.cc($|/.*\?|/.*$|/)', url) != None:
                    if '&page=' in url:
                        url = url.split('&page=')[0] + '&'
                    elif '?page=' in url:
                        url = url.split('?page=')[0] + '?'
                    elif re.match('.*favorites($|/$)', url):
                        start_time = time.time()
                        print('正在爬取收藏中...')
                        favorites_url_list = parse_favorites(url.rstrip())
                        end_time = time.time()
                        print('\033[0;37;42m耗时%f秒\033[0m' % (end_time - start_time))
                    elif url.rstrip()[-1] == '/':
                        url = url[:-1] + '?'
                    else:
                        url = url.rstrip() + '?'
                    break
                print('\033[0;37;41m你输入的网址有误，请重新输入！\033[0m')
            break
        elif choice == '6':
            txt_spider()
            return
        else:
            print('\033[0;37;41m请输入正确的序号！\033[0m')
            continue
    print(url)
    spider(url, name)


def spider(url='', name='', flag=True):
    global favorites_url_list
    global count
    global url_list
    global sum
    global retry_num
    global time_out_retry_num
    name = name.replace('\\', '').replace('/', '').replace(':', '').replace('*', '').replace('?', '').replace('"',
                                                                                                              '').replace(
        '<', '').replace('>', '').replace('|', '')
    start_page, page = get_page()
    if not os.path.exists('img'):
        os.mkdir('img')
    if (favorites_url_list != []):
        favorites_url_list = favorites_url_list[start_page:page]
        favorites_index = start_page
        for i in favorites_url_list:
            name, url = i
            print('正在爬取第' + str(favorites_index + 1) + '个：' + name)
            if (favorites_index < page + 1):
                favorites(name, url)
            url_list = []
            count = 0
            favorites_index += 1
    else:
        url_lists = []
        for i in range(start_page, page):
            url_lists.append(url + 'page=' + str(i + 1))
        sum = page - start_page
        with lock:
            print('开始爬取...')
        start_time = time.time()
        count = 0
        retry_num = 0
        if thread:
            pool.map(parse_mul, url_lists)
        else:
            parse(url, start_page, page)
        sum = len(url_list)
        if sum == 0 and flag:
            with lock:
                print('\033[0;37;41m没有匹配的结果，换个关键词试试吧！\033[0m')
            main()
        end_time = time.time()
        with lock:
            print('\n爬取完毕')
            print('\033[0;37;42m耗时%f秒\033[0m' % (end_time - start_time))
        if output:
            to_txt(url_list)
            if flag:
                with lock:
                    print('感谢您的使用！')
                    input('按Enter键退出')
                sys.exit()
        url_lists = [(name, url) for url in url_list]
        with lock:
            print('开始下载')
        if not os.path.exists('img/' + name + '/'):
            os.mkdir('img/' + name + '/')
        start_time = time.time()
        count = 0
        retry_num = 0
        time_out_retry_num = 0
        pool.map(img_download, url_lists)
        with lock:
            print('\n下载完成')
            end_time = time.time()
            print('\033[0;37;42m耗时%f秒\033[0m' % (end_time - start_time))
    if flag:
        with lock:
            print('感谢您的使用！')
            input('按Enter键退出')


if __name__ == '__main__':
    main()
