# -*- coding:utf-8 -*-

'''
爬取糗事百科主页及分页的主要内容
'''

import json
import re
from multiprocessing import Pool

import chardet
import requests
from bs4 import BeautifulSoup
from requests import RequestException

url = 'http://www.qiushibaike.com'
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
}


def get_page_text(url):
    global content
    try:
        content = requests.get(url, headers=headers)
        content.encoding = 'utf-8'
        if content.status_code == 200:
            # print(content.text)
            return content.text
        else:
            return None
    except RequestException as e:
        print('请求错误:' + str(e))
        return None


def get_item_name(names):
    for name in names:
        name = re.findall(r"\S+", name.text)
        return name[0].strip()


def get_item_detail(details):
    for detail in details:
        detail = re.findall(r"\S+", detail.text)
        return "".join(detail)


def get_vote_num(vote_nums):
    for num in vote_nums:
        num = re.findall(r"\S+", num.text)
        return num[0]


def parse_item_page(result):
    for item in result:
        if item.select('.thumb'):
            continue
        else:
            names = item.select('.author')
            name = get_item_name(names)
            # print(name)
            details = item.select('.content')
            detail = get_item_detail(details)
            # print(content)
            vote_nums = item.select('.stats-vote')
            vote_num = get_vote_num(vote_nums)
            # print(vote_num)
            yield {
                'name': name,
                'content': detail,
                'vote_num': vote_num
            }


def write_to_file(detail):
    try:
        with open('result.txt', 'a')as f:
            f.write(json.dumps(detail, ensure_ascii=False) + '\n\n')
            f.close()
        file = open('result.txt', 'rb')
        data = file.read()
        print(chardet.detect(data))
    except Exception as e:
        print('写入失败:' + str(e))


def get_page_url(page_num):
    if page_num > 1:
        return (url + '/8hr/page/{}/').format(str(page_num))
    else:
        return url


def main(page_num):
    page_url = get_page_url(page_num)
    print(page_url)
    response = get_page_text(page_url)
    soup = BeautifulSoup(response, "html.parser")
    result = soup.find_all(id=re.compile('qiushi_tag'))
    for item in parse_item_page(result):
        # print(type(item))
        write_to_file(item)


if __name__ == '__main__':
    groups = [x for x in range(1, 14)]
    pool = Pool()
    # try:
    pool.map(main, groups)
    # except TypeError:
    pool.close()
    pool.join()
