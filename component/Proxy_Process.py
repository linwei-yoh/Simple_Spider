#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = 'AL'

from multiprocessing import Process
import time
from concurrent.futures import ThreadPoolExecutor

from ProxyPool import *
from utilities.util_fetch import make_random_useragent
import requests
from Redis_Helper import RedisClient
from logger_config import report_logger

TEST_URL = "http://house.ksou.cn/"
MinSize = 500


class ProxyPoolProcess(Process):
    def __init__(self,CN=True):
        Process.__init__(self, name='Proxy')
        self.daemon = True
        self.china = CN

    def run(self):
        if self.china:
            self.ProxySites = [bugng(), xiciSpider(), kuaidaili(), superfastip(), sixsixip()]
        else:
            self.ProxySites = [ProxyNova()]
        self.client = RedisClient()
        try:
            self._run()
        except Exception as exc:
            report_logger.error(str(exc))

    def _run(self):
        while True:
            if self.client.proxy_list_size() < MinSize:
                proxy_list = self.get_proxy()
                if len(proxy_list) > 0:
                    self.check_save_proxy(proxy_list)
            time.sleep(1)

    def get_proxy(self):
        proxy_list = []

        for proxySite in self.ProxySites:
            proxy_list.extend(proxySite.get_proxy_ip())

        return proxy_list

    def check_save_proxy(self, proxy_list):
        with ThreadPoolExecutor(max_workers=20) as executor:
            for proxy in proxy_list:
                executor.submit(self.proxy_test, proxy).add_done_callback(self.proxy_test)

    def proxy_test(self, proxy):
        try:
            proxies = {
                "http": "http://" + proxy[0],
                "https": "http://" + proxy[0],
            }
            header = {'User-Agent': make_random_useragent()}
            r = requests.get(TEST_URL, headers=header, proxies=proxies, timeout=(6.05, 10))
        except Exception:
            return None
        else:
            if r.status_code == 200:
                self.client.insert_proxy_set(proxy[0])
            else:
                return None


if __name__ == '__main__':
    proxy_T = ProxyPoolProcess()
    proxy_T.start()
    proxy_T.join()
    pass
