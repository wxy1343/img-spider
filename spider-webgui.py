import json
import os
import socket
import random
import sys
import time
import webbrowser
import urllib.parse
from threading import Thread

import requests

from config import *
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as ThreadPool

from req import Req

thread = True
threads_num = 100
retry = True
retry_max = 2
retry_num = 0
output = False
sum = 0
count = 0
s1 = None
s2 = None
s3 = None
s4 = None
s5 = None
s6 = None
url_list = []
HTML_ROOT_DIR = ''
requests.packages.urllib3.disable_warnings()


def handle_client(client_socket):
    request_data = client_socket.recv(1024)
    if not b'' == request_data:
        # print('*' * 10)
        # print(request_data.decode())
        # print('*' * 10)
        method = request_data.decode().splitlines()[0].split()[0]
        print(method)
        if method == 'GET':
            file_name = request_data.decode().splitlines()[0].split()[1]
            if file_name == '/':
                file_name = 'index.html'
            else:
                file_name = file_name[1:]
            print(file_name)
            response_start_line = 'HTTP/1.1 200 OK\r\n'
            response_headers = 'Server: Python\r\n'
            try:
                with open(HTML_ROOT_DIR + file_name, 'rb') as f:
                    response_body = f.read().decode()
            except OSError:
                response_start_line = 'HTTP/1.1 404 Not Found\r\n'
                response_body = 'The file is not found!'
            response = response_start_line + response_headers + '\r\n' + response_body
            client_socket.send(response.encode())
            client_socket.close()
        elif method == 'POST':
            data_dict = {}
            uri = request_data.decode('utf-8').splitlines()[0].split()[1][1:]
            print(uri)
            if not request_data.decode('utf-8').splitlines()[-1] == '':
                for i in request_data.decode('utf-8').splitlines()[-1].split('&'):
                    key = i.split('=')[0]
                    value = i.split('=')[1]
                    data_dict[key] = urllib.parse.unquote(value)
                print(data_dict)
                # client_socket.send(json.dumps(data).encode())
            global thread
            global threads_num
            global retry
            global retry_max
            global output
            global sum
            global count
            global s1
            global s2
            global s3
            global s4
            global s5
            global s6
            configdir = 'config.ini'
            cf = Config(configdir, '配置')
            if uri == 'set':
                data = {}
                thread = data['thread'] = cf.GetBool('配置', 'thread')
                threads_num = data['threads_num'] = cf.GetInt('配置', 'threads_num')
                retry = data['retry'] = cf.GetBool('配置', 'retry')
                retry_max = data['retry_max'] = cf.GetInt('配置', 'retry_max')
                output = data['output'] = cf.GetBool('配置', 'output')
                client_socket.send(json.dumps(data).encode())
            elif uri == 'option':
                thread = str_to_bool(data_dict['thread'])
                cf.Update('配置', 'thread', str(thread))
                threads_num = int(data_dict['threads_num'])
                cf.Update('配置', 'threads_num', str(threads_num))
                retry = str_to_bool(data_dict['retry'])
                cf.Update('配置', 'retry', str(retry))
                retry_max = int(data_dict['retry_max'])
                cf.Update('配置', 'retry_max', str(retry_max))
                output = str_to_bool(data_dict['output'])
                cf.Update('配置', 'output', str(output))
                data = {'msg': 'ok'}
                client_socket.send(json.dumps(data).encode())
            elif uri == '1':
                key = data_dict['key']
                strat_page = int(data_dict['start']) - 1
                end_page = int(data_dict['end'])
                url = 'https://wallhaven.cc/search?q=' + key + '&'
                s1 = Spider(url, strat_page, end_page)
                s1.name = remove_special_character(key)
                t1 = Thread(target=s1.img_spider)
                t1.start()
                data = {'msg': 'ok'}
                client_socket.send(json.dumps(data).encode())
            elif uri == '1.status':
                if s1 != None and s1.sum != 0:
                    data = {'count': s1.count, 'sum': s1.sum}
                    client_socket.send(json.dumps(data).encode())
            elif uri == '1.download':
                t1 = Thread(target=download, args=(s1,))
                t1.start()
            elif uri == '1.download.status':
                if s1.sum != 0:
                    data = {'count': s1.count, 'sum': s1.sum}
                    client_socket.send(json.dumps(data).encode())
            elif uri == '2':
                strat_page = int(data_dict['start']) - 1
                end_page = int(data_dict['end'])
                url = 'https://wallhaven.cc/latest?'
                s2 = Spider(url, strat_page, end_page)
                s2.name = 'latest'
                t2 = Thread(target=s2.img_spider)
                t2.start()
                data = {'msg': 'ok'}
                client_socket.send(json.dumps(data).encode())
            elif uri == '2.status':
                if s2 != None and s2.sum != 0:
                    data = {'count': s2.count, 'sum': s2.sum}
                    client_socket.send(json.dumps(data).encode())
            elif uri == '2.download':
                t2 = Thread(target=download, args=(s2,))
                t2.start()
            elif uri == '2.download.status':
                if s2.sum != 0:
                    data = {'count': s2.count, 'sum': s2.sum}
                    client_socket.send(json.dumps(data).encode())
            elif uri == '3':
                strat_page = int(data_dict['start']) - 1
                end_page = int(data_dict['end'])
                url = 'https://wallhaven.cc/toplist?'
                s3 = Spider(url, strat_page, end_page)
                s3.name = 'toplist'
                t3 = Thread(target=s3.img_spider)
                t3.start()
                data = {'msg': 'ok'}
                client_socket.send(json.dumps(data).encode())
            elif uri == '3.status':
                if s3 != None and s3.sum != 0:
                    data = {'count': s3.count, 'sum': s3.sum}
                    client_socket.send(json.dumps(data).encode())
            elif uri == '3.download':
                t3 = Thread(target=download, args=(s3,))
                t3.start()
            elif uri == '3.download.status':
                if s3.sum != 0:
                    data = {'count': s3.count, 'sum': s3.sum}
                    client_socket.send(json.dumps(data).encode())
            elif uri == '4':
                rand = data_dict['rand']
                strat_page = int(data_dict['start']) - 1
                end_page = int(data_dict['end'])
                url = 'https://wallhaven.cc/random?seed=' + rand + '&'
                s4 = Spider(url, strat_page, end_page)
                s4.name = remove_special_character(rand)
                t4 = Thread(target=s4.img_spider)
                t4.start()
                data = {'msg': 'ok'}
                client_socket.send(json.dumps(data).encode())
            elif uri == '4.status':
                if s4 != None and s4.sum != 0:
                    data = {'count': s4.count, 'sum': s4.sum}
                    client_socket.send(json.dumps(data).encode())
            elif uri == '4.download':
                t4 = Thread(target=download, args=(s4,))
                t4.start()
            elif uri == '4.download.status':
                if s4.sum != 0:
                    data = {'count': s4.count, 'sum': s4.sum}
                    client_socket.send(json.dumps(data).encode())
            elif uri == '5':
                url = data_dict['url'] + '&'
                strat_page = int(data_dict['start']) - 1
                end_page = int(data_dict['end'])
                s5 = Spider(url, strat_page, end_page)
                s5.name = ''
                t5 = Thread(target=s5.img_spider)
                t5.start()
                data = {'msg': 'ok'}
                client_socket.send(json.dumps(data).encode())
            elif uri == '5.status':
                if s5 != None and s5.sum != 0:
                    data = {'count': s5.count, 'sum': s5.sum}
                    client_socket.send(json.dumps(data).encode())
            elif uri == '5.download':
                t5 = Thread(target=download, args=(s5,))
                t5.start()
            elif uri == '5.download.status':
                if s5.sum != 0:
                    data = {'count': s5.count, 'sum': s5.sum}
                    client_socket.send(json.dumps(data).encode())
            elif uri == '6.download':
                s6 = Spider()
                s6.path = data_dict['path']
                s6.name = ''
                try:
                    s6.url_list = read_txt(s6.path)
                except IOError:
                    data = {'msg': 'IOError'}
                    client_socket.send(json.dumps(data).encode())
                    return
                t6 = Thread(target=txt_download, args=(s6,))
                t6.start()
            elif uri == '6.download.status':
                if s6.sum != 0:
                    data = {'count': s6.count, 'sum': s6.sum}
                    client_socket.send(json.dumps(data).encode())
            else:
                data = {'msg': 'fail'}
                client_socket.send(json.dumps(data).encode())


def init():
    global thread
    global threads_num
    global retry
    global retry_max
    global output
    configdir = 'config.ini'
    if not os.path.exists(configdir):
        f = open(configdir, 'a')
        f.close()
        cf = Config(configdir, '配置')
        cf.Add('配置', 'thread', str(thread))
        cf.Add('配置', 'threads_num', str(threads_num))
        cf.Add('配置', 'retry', str(retry))
        cf.Add('配置', 'retry_max', str(retry_max))
        cf.Add('配置', 'output', str(output))
    else:
        cf = Config(configdir)
        thread = cf.GetBool('配置', 'thread')
        threads_num = cf.GetInt('配置', 'threads_num')
        retry = cf.GetBool('配置', 'retry')
        retry_max = cf.GetInt('配置', 'retry_max')
        output = cf.GetBool('配置', 'output')
    if not thread:
        threads_num = 1


def read_txt(path):
    list = []
    with open(path, 'r') as f:
        for i in f.readlines():
            if i != '':
                list.append(i.strip().replace('\n', '').replace('\r', ''))
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


def str_to_bool(str):
    return True if str.lower() == 'true' else False


def remove_special_character(str):
    str.replace('\\', '').replace('/', '').replace(':', '').replace('*', '').replace('?',
                                                                                     '').replace(
        '"',
        '').replace(
        '<', '').replace('>', '').replace('|', '')
    return str


def txt_download(obj):
    obj.url_list = list(set(obj.url_list))
    obj.sum = len(obj.url_list)
    print('*' * 50)
    if obj.sum == 0:
        print('\033[0;37;41m文件没有内容！\033[0m')
        data = {'msg': 'no content'}
        client_socket.send(json.dumps(data).encode())
        return
    data = {'msg': 'ok'}
    client_socket.send(json.dumps(data).encode())
    if not os.path.exists('img/' + obj.name + '/'):
        os.mkdir('img/' + obj.name + '/')
    url_lists = [(obj, url) for url in obj.url_list]
    obj.count = 0
    obj.retry_num = 0

    @Retry_parameter(obj)
    def download():
        ThreadPool(threads_num).map(img_download, url_lists)


def download(obj):
    obj.sum = len(obj.url_list)
    if (obj.sum == 0):
        print('\033[0;37;41m没有匹配的结果，换个关键词试试吧！\033[0m')
        data = {'msg': 'no match'}
        client_socket.send(json.dumps(data).encode())
        return
    data = {'msg': 'ok'}
    client_socket.send(json.dumps(data).encode())
    url_lists = [(obj, url) for url in obj.url_list]
    if not os.path.exists('img/' + obj.name + '/'):
        os.mkdir('img/' + obj.name + '/')
    obj.count = 0
    obj.retry_num = 0

    @Retry_parameter(obj)
    def download():
        ThreadPool(threads_num).map(img_download, url_lists)


def img_download(args):
    obj, url = args
    if obj.name != '':
        path = 'img/' + obj.name + '/'
    else:
        path = 'img/'
    global count
    if os.path.exists(path + url[-10:]) == True:
        temp_size = os.path.getsize(path + url[-10:])
    elif os.path.exists(path + (url[:-4] + '.png')[-10:]) == True:
        temp_size = os.path.getsize(path + (url[:-4] + '.png')[-10:])
    else:
        temp_size = 0
    headers = {'Range': 'bytes=%d-' % temp_size}
    r = requests.get(url, stream=True, verify=False, headers=headers)
    while r.status_code == 503:
        r = requests.get(url, stream=True, verify=False, headers=headers)
    if (r.status_code == 404):
        url = url[:-4] + '.png'
        r = requests.get(url, stream=True, verify=False, headers=headers)
        while r.status_code == 503:
            r = requests.get(url, stream=True, verify=False, headers=headers)
    with open(path + url[-10:], "ab") as f:
        for chunk in r.iter_content(chunk_size=128):
            if chunk:
                temp_size += len(chunk)
                f.write(chunk)
                f.flush()
    progress_bar(obj)


class Spider:
    def __init__(self, url='', strat_page=1, end_page=1):
        self.url = url
        self.start_page = strat_page
        self.end_page = end_page
        self.url_lists = []
        self.url_list = []
        self.sum = 0
        self.count = 0
        self.retry_num = 0
        self.strat_page = strat_page
        self.end_page = end_page

    def img_spider(self):
        if not os.path.exists('img'):
            os.mkdir('img')
        for i in range(self.start_page, self.end_page):
            self.url_lists.append(self.url + 'page=' + str(i + 1))
        self.url_lists = [(self, url) for url in self.url_lists]
        self.sum = self.end_page - self.start_page
        self.count = 0
        self.retry_num = 0

        @Retry_parameter(self)
        def spider():
            ThreadPool(threads_num).map(parse_mul, self.url_lists)
            print()

        if output:
            to_txt(self.url_list)


def parse_mul(args):
    obj, url = args
    req = Req()
    response = req.get(url)
    soup = BeautifulSoup(response.text, features='lxml')
    for j in soup.find_all('figure'):
        urls = 'https://w.wallhaven.cc/full/' + j['data-wallpaper-id'][:2] + '/wallhaven-' + j[
            'data-wallpaper-id'] + '.jpg'
        if urls not in obj.url_list:
            obj.url_list.append(urls)
    progress_bar(obj)


def Retry_parameter(obj):
    def Retry(f):
        while True:
            try:
                f()
            except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError):
                print('\n\033[0;37;41m远程主机强迫关闭了一个现有的连接。\033[0m')
                if (retry and (obj.retry_num < retry_max)):
                    obj.retry_num += 1
                    print('第%d次重试' % obj.retry_num)
                    obj.count = 0
                else:
                    print('\n下载失败')
            else:
                break

    return Retry


def progress_bar(obj):
    obj.count += 1
    done = int(50 * obj.count / obj.sum)
    char = '╱╲'
    sys.stdout.write("\r\033[0;37;42m    %s%s：%d%%|%s%s| %d/%d\033[0m" % (
        char[obj.count % 2], '进度', 100 * obj.count / obj.sum, '█' * done, ' ' * (50 - done), obj.count, obj.sum))
    sys.stdout.flush()


def port_used(port, ip='127.0.0.1'):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, port))
        s.shutdown(2)
        return True
    except:
        return False


if __name__ == '__main__':
    init()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 80
    host = 'http://127.0.0.1:' + str(port)
    while port_used(port):
        port = random.randint(1, 65535)
    host = 'http://127.0.0.1:' + str(port)
    s.bind(('', port))
    print(host)
    webbrowser.open(host)
    s.listen()
    while True:
        client_socket, socket_address = s.accept()
        print('*' * 10)
        print('%s:%s' % socket_address)
        handle_client(client_socket)
        client_socket.close()
