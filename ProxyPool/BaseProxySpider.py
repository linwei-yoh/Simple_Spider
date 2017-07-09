#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = 'AL'


from concurrent.futures import ThreadPoolExecutor
import requests
from concurrent import futures
from utilities.util_fetch import make_random_useragent
from datetime import datetime

from enum import Enum


# HTTP_X_FORWARDED_FOR
class ProxyType(Enum):
    Transparent = 0     # 透明代理 HTTP_X_FORWARDED_FOR 为自己IP
    Anonymous = 1       # 匿名代理 HTTP_X_FORWARDED_FOR 代理IP 但仍然知道是代理
    Distorting = 2      # 混淆代理 HTTP_X_FORWARDED_FOR = Random IP address
    Elite = 3           # 高匿代理 HTTP_VIA = not determined;HTTP_X_FORWARDED_FOR = not determined



class BaseProxySpider(object):
    name = 'gatherproxy'

    def __init__(self):
        self.urls = [
            'http://gatherproxy.com/',
            'http://www.gatherproxy.com/proxylist/anonymity/?t=Anonymous',
            'http://gatherproxy.com/proxylist/country/?c=China',
        ]

        self.headers = {'User-Agent': make_random_useragent()}
        self.last_time = None
        self.interval = 60 * 10  # 10分钟

    def get_proxy_ip(self):
        if self.last_time is None:
            self.last_time = datetime.now()
            return self.spider_working()
        elif self.interval == "Never":
            return []
        elif (datetime.now() - self.last_time).total_seconds() >= self.interval:
            self.last_time = datetime.now()
            return self.spider_working()
        else:
            return []

    def spider_working(self):
        futures_list = list()
        result_list = list()
        with ThreadPoolExecutor() as executor:
            for url in self.urls:
                future = executor.submit(self.url_fetch, url)
                futures_list.append(future)
            try:
                for future in futures.as_completed(futures_list):
                    result_list.extend(future.result())
            except Exception:
                return []
        return result_list

    def url_fetch(self, url):
        try:
            r = requests.get(url, headers=self.headers, timeout=(6.05, 10))
        except Exception:
            return []
        else:
            if r.status_code == 200:
                return self.parse_page(r.text)
            else:
                return []

    # IP:端口, 代理类型(Http/Https), 匿名性,  录入时间, 响应时间, 代理所在地
    def parse_page(self, response):
        proxy_list = list()
        return proxy_list


if __name__ == '__main__':

    pass
