#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = 'AL'

from BaseProxySpider import BaseProxySpider, ProxyType
import logging
import json
from utilities.util_fetch import make_random_useragent


class bugng(BaseProxySpider):
    name = '虫代理'

    def __init__(self):
        BaseProxySpider.__init__(self)
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
            'Host': 'www.bugng.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': make_random_useragent()
        }
        self.urls = ["http://www.bugng.com/api/getproxy/json?num=80&anonymity=1&type=0"]
        self.interval = 30   # 0.5分钟

    def parse_page(self, response):
        proxy_list = list()
        # re正则取出数据
        try:
            if response == "":
                return []
            json_data = json.loads(response)
            if json_data['code'] == -1:
                return []
            proxy_item_list = json_data["data"]["proxy_list"]
            for proxy_item in proxy_item_list:
                # IP:PORT,匿名性,代理类型,录入时间,响应时间,代理所在地,来源
                proxy_list.append([proxy_item, "HTTP",ProxyType.Elite, None, None, "中国",self.name])
        except Exception as e:
            logging.error("%s 爬取出错" % self.name, e)
            return []
        else:
            return proxy_list


if __name__ == '__main__':
    proxy_client = bugng()
    result = proxy_client.get_proxy_ip()
    for item in result:
        print(item)
    pass
