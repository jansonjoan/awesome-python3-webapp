# -*- coding:utf-8 -*-
import random
import re
from lxml import etree

import requests
from bs4 import BeautifulSoup
import subprocess as sp


class Proxys(object):
    def __init__(self, page=1):
        # requests的Session可以自动保持cookie,不需要自己维护cookie内容
        self.S = requests.Session()
        # 西祠代理高匿IP地址
        self.target_url = 'http://www.xicidaili.com/nn/%d' % page
        # 完善的headers
        self.target_headers = {
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Referer': 'http://www.xicidaili.com/nn/',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }

    """
    函数说明:获取IP代理
    Parameters:
        page - 高匿代理页数,默认获取第一页
    Returns:
        proxys_list - 代理列表
    Modify:
        2018-01-31
    """

    def get_proxys(self):
        try:
            # get请求
            target_response = self.S.get(url=self.target_url, headers=self.target_headers)
            # utf-8编码
            target_response.encoding = 'utf-8'
            # 获取网页信息
            target_html = target_response.text
            # 获取id为ip_list的table
            bf1_ip_list = BeautifulSoup(target_html, 'lxml')
            bf2_ip_list = BeautifulSoup(str(bf1_ip_list.find_all(id='ip_list')), 'lxml')
            ip_list_info = bf2_ip_list.table.contents
            # 存储代理的列表
            proxys_list = []
            # 爬取每个代理信息
            for index in range(len(ip_list_info)):
                if index % 2 == 1 and index != 1:
                    dom = etree.HTML(str(ip_list_info[index]))
                    ip = dom.xpath('//td[2]')
                    port = dom.xpath('//td[3]')
                    protocol = dom.xpath('//td[6]')
                    proxys_list.append(protocol[0].text.lower() + '#' + ip[0].text + '#' + port[0].text)
            # 返回代理列表
            return proxys_list
        except AttributeError:
            return None

    """
    函数说明:检查代理IP的连通性
    Parameters:
        ip - 代理的ip地址
        lose_time - 匹配丢包数
        waste_time - 匹配平均时间
    Returns:
        average_time - 代理ip平均耗时
    Modify:
        2018-01-31
    """

    def check_ip(self, ip):
        # 命令 -n 要发送的回显请求数 -w 等待每次回复的超时时间(毫秒)
        cmd = 'ping -n 3 -w 3 %s'
        # 执行命令
        p = sp.Popen(cmd % ip, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        # 获得返回结果并解码
        out = p.stdout.read().decode('gbk')
        # 丢包数,平均时间
        lose_time, waste_time = self.initpattern(out)
        print(lose_time, waste_time)
        # 当匹配到丢失包信息失败,默认为三次请求全部丢包,丢包数lose赋值为3
        if len(lose_time) == 0:
            lose = 3
        else:
            lose = int(lose_time[0])
        if lose > 2:
            return 1000
        else:
            if len(waste_time) == 0:
                return 1000
            else:
                average_time = int(waste_time[0])
                return average_time

    def initpattern(self, output):
        lose_time = re.compile(u'丢失 = (\d+)', re.IGNORECASE).findall(output)
        waste_time = re.compile(u'平均 = (\d+)ms', re.IGNORECASE).findall(output)
        return lose_time, waste_time

    def get_proxy(self):
        proxy_dicts = []
        proxys_list = self.get_proxys()
        # if len(proxys_list) > 0:
        try:
            while len(proxys_list) > 90:
                proxy = random.choice(proxys_list)
                split_proxy = proxy.split('#')
                ip = split_proxy[1]
                average_time = self.check_ip(ip)
                if average_time > 200:
                    proxys_list.remove(proxy)
                    print(ip + '连接超时,ip重新获取中')
                if average_time < 200:
                    proxys_list.remove(proxy)
                    proxy_dict = {split_proxy[0]: split_proxy[1] + ':' + split_proxy[2]}
                    proxy_dicts.append(proxy_dict)
                    print('使用代理:', proxy_dicts)
                    # continue
            return proxy_dicts
        except Exception as e:
            print(proxy_dicts, e)
            return proxy_dicts


if __name__ == '__main__':
    proxys = Proxys(2)
    proxys.get_proxy()
