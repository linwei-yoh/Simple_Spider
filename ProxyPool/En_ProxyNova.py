#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = 'AL'

from utilities.util_fetch import make_random_useragent
from BaseProxySpider import BaseProxySpider, ProxyType
import logging
from pyquery import PyQuery as pq
import re


class ProxyNova(BaseProxySpider):
    name = 'ProxyNova'

    def __init__(self):
        BaseProxySpider.__init__(self)
        self.headers = {
            'User-Agent': make_random_useragent()
        }
        self.urls = ["https://www.proxynova.com/proxy-server-list/elite-proxies/"]
        self.interval = 65

    def parse_page(self, response):
        proxy_list = list()

        try:
            doc = pq(response)
            table_node = doc("#tbl_proxy_list")
            item_nodes = table_node("tbody")("tr")
            for item in item_nodes.items():
                info_nodes = item("td:lt(2)")
                if len(info_nodes) < 2:
                    continue
                try:
                    proxy_item = [i.text() for i in info_nodes.items('td')]
                    params = re.findall(r"\D+([\d\\.]+)\D+(\d+)\D+([\d\\.]+)", proxy_item[0])[0]
                    ipstr1 = params[0]
                    ippos = int(params[1])
                    ipstr2 = params[2]
                    ip = ipstr1[ippos:] + ipstr2 + ":" + proxy_item[1]
                    # IP:端口, 代理类型(Http/Https), 匿名性,  录入时间, 响应时间, 代理所在地
                    result.append([ip, "None", ProxyType.Elite, "None", "None", "None", self.name])
                except Exception:
                    pass
        except Exception as e:
            logging.error("%s 爬取出错" % self.name, e)
            return []
        else:
            return proxy_list


if __name__ == '__main__':
    proxy_client = ProxyNova()
    result = proxy_client.get_proxy_ip()
    for item in result:
        print(item)
    pass
