#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = 'AL'

from BaseProxySpider import BaseProxySpider, ProxyType
import re
from utilities.util_fetch import make_random_useragent
import logging


class superfastip(BaseProxySpider):
    name = 'superfast'

    def __init__(self):
        BaseProxySpider.__init__(self)
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
            'Host': 'superfastip.com',
            'Upgrade-Insecure-Requests': '1',
            "Referer": "http://superfastip.com/welcome/getips",
            'User-Agent': make_random_useragent()
        }
        self.urls = ["http://superfastip.com/welcome/getips/1",
                     "http://superfastip.com/welcome/getips/2"]

    def parse_page(self, response):
        proxy_list = list()
        # re正则取出数据
        try:
            response = response.encode('ISO-8859-1').decode()
            re_list_item = re.findall(r'<tr>(.*?)</tr>', response, re.S)
            l = len(re_list_item)
            for i in range(l):
                atts = re.findall(r'<td>(.*?)</td>', re_list_item[i], re.S)
                # IP:端口, 代理类型(Http/Https), 匿名性,  录入时间, 响应时间, 代理所在地
                list_i = [atts[1]+":"+atts[2],  # IP:端口
                          atts[5],  # 代理类型
                          ProxyType.Elite,  # 匿名性
                          atts[7],  # 录入时间
                          atts[6],  # 响应时间
                          atts[0],  # 代理所在地
                          self.name] # 代理来源
                proxy_list.append(list_i)
        except Exception as e:
            logging.error("%s 爬取出错" % self.name, e)
            return []
        else:
            return proxy_list


if __name__ == '__main__':
    proxy_client = superfastip()
    result = proxy_client.get_proxy_ip()
    for item in result:
        print(item)
    pass
