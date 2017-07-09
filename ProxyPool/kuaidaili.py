#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = 'AL'

from utilities.util_fetch import make_random_useragent
from BaseProxySpider import BaseProxySpider, ProxyType
import logging
from pyquery import PyQuery as pq


class kuaidaili(BaseProxySpider):
    name = '快代理'

    def __init__(self):
        BaseProxySpider.__init__(self)
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
            'Host': 'www.kuaidaili.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': make_random_useragent()
        }
        self.urls = ["http://www.kuaidaili.com/free/inha/1/",
                     "http://www.kuaidaili.com/free/inha/2/",
                     "http://www.kuaidaili.com/free/inha/3/",
                     "http://www.kuaidaili.com/free/outha/1/",
                     "http://www.kuaidaili.com/free/outha/2/",
                     "http://www.kuaidaili.com/free/outha/3/"]
        self.interval = "Never"  # 只爬取一次

    def parse_page(self, response):
        proxy_list = list()

        try:
            doc = pq(response)
            item_list_node = doc('tr:gt(0)')

            for proxy_item in item_list_node.items():
                atts = [att.text() for att in proxy_item("td").items()]
                # IP:端口, 代理类型(Http/Https), 匿名性,  录入时间, 响应时间, 代理所在地
                country, *_ = atts[4].split(' ', 1)
                proxy_list.append([atts[0] + ":" + atts[1], atts[3], ProxyType.Elite, atts[6], atts[5], country,self.name])
        except Exception as e:
            logging.error("%s 爬取出错" % self.name, e)
            return []
        else:
            return proxy_list


if __name__ == '__main__':
    proxy_client = kuaidaili()
    result = proxy_client.get_proxy_ip()
    for item in result:
        print(item)
    pass
