#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = 'AL'

from BaseProxySpider import BaseProxySpider, ProxyType
import re
from utilities.util_fetch import make_random_useragent
import logging

class xiciSpider(BaseProxySpider):
    name = 'xicidaili'

    def __init__(self):
        BaseProxySpider.__init__(self)
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
            'Host': 'www.xicidaili.com',
            'Upgrade-Insecure-Requests': '1',
            "Referer": "http://www.xicidaili.com/",
            'User-Agent': make_random_useragent()
        }
        self.urls = ["http://www.xicidaili.com/nn/1",
                     "http://www.xicidaili.com/nn/2",
                     "http://www.xicidaili.com/nn/3",
                     "http://www.xicidaili.com/nn/4"]

    def parse_page(self, response):
        proxy_list = list()
        # re正则取出数据
        try:
            re_list_ip = re.findall(r'<td>(\d*\.\d*\.\d*\.\d*)</td>', response)
            re_list_port = re.findall(r'<td>([\d]*)</td>', response)
            re_list_type = re.findall(r'<td>([A-Za-z]*)</td>', response)
            re_list_time = re.findall(r'<td>(\d*-\d*-\d* \d*:\d*)</td>', response)
            re_list_response = re.findall(r'title="([\d\.]*)秒"', response)

            l = len(re_list_ip)
            for i in range(l):
                PROXY_IP = re_list_ip[i]
                PROXY_PORT = re_list_port[i]
                PROXY_COUNTRY = 'China'
                AnonymityType = ProxyType.Elite
                Addtime = re_list_time[i]
                ResponseTime = round(float(re_list_response[i]), 2)
                PROXY_TYPE = re_list_type[i]

                # IP:端口, 代理类型(Http/Https), 匿名性,  录入时间, 响应时间, 代理所在地
                list_i = [PROXY_IP+":"+PROXY_PORT, PROXY_TYPE , AnonymityType, Addtime, ResponseTime, PROXY_COUNTRY,self.name]
                proxy_list.append(list_i)
        except Exception as e:
            logging.error("%s 爬取出错" % self.name, e)
            return []
        else:
            return proxy_list


if __name__ == '__main__':
    proxy_client = xiciSpider()
    result = proxy_client.get_proxy_ip()
    for item in result:
        print(item)
    pass
