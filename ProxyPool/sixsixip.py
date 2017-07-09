#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = 'AL'

from BaseProxySpider import BaseProxySpider, ProxyType
import re
from utilities.util_fetch import make_random_useragent
import logging
from datetime import datetime


class sixsixip(BaseProxySpider):
    name = '66ip'

    def __init__(self):
        BaseProxySpider.__init__(self)
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
            'Host': 'www.66ip.cn',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': make_random_useragent()
        }
        self.urls = [
            "http://www.66ip.cn/nmtq.php?"
            "getnum=200&"
            "isp=1&"
            "anonymoustype=3&"
            "start=&ports=&export=&ipaddress=&area=0&proxytype=0&"
            "api=66ip"]

    def parse_page(self, response):
        proxy_list = list()
        # re正则取出数据
        try:
            re_list_proxy = re.findall(r'(\d*\.\d*\.\d*\.\d*:\d*)', response)

            l = len(re_list_proxy)
            for i in range(l):
                PROXY_RECORD = re_list_proxy[i]
                PROXY_COUNTRY = 'China'
                AnonymityType = ProxyType.Elite
                Addtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ResponseTime = None
                PROXY_TYPE = "HTTP"

                # IP:端口, 代理类型(Http/Https), 匿名性,  录入时间, 响应时间, 代理所在地
                list_i = [PROXY_RECORD, PROXY_TYPE, AnonymityType, Addtime, ResponseTime, PROXY_COUNTRY, self.name]
                proxy_list.append(list_i)
        except Exception as e:
            logging.error("%s 爬取出错" % self.name, e)
            return []
        else:
            return proxy_list


if __name__ == '__main__':
    proxy_client = sixsixip()
    result = proxy_client.get_proxy_ip()
    for item in result:
        print(item)
    pass
