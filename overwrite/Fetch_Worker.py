#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = 'AL'

from component.Fetch_Thread import FetchWorker
from component.logger_config import report_logger

import time
import requests
from utilities import make_random_useragent

ksou_Header = {'Host': 'www.ksouhouse.com',
               'Referer': 'http://www.ksouhouse.com/index.php'}

ksou_params = {"agent": "0", "count": "300", "htype": "", "lat": "0", "lng": "0", "maxbed": "0", "maxprice": "0",
               "minbed": "0", "minprice": "0", "p": "0", "q": "Mount Waverley", "region": "Mount Waverley",
               "s": "1", "st": "", "sta": "vic", "type": ""}


class RpFetchWorker(FetchWorker):
    def __init__(self, session, max_repeat):
        FetchWorker.__init__(self, max_repeat)
        self.session = session

    def url_fetch(self, params, proxy):
        try:
            fetch_result, content = self.working(params, proxy)
        except Exception:
            repeat = params["Repeat"]
            if repeat >= self.max_repeat:
                fetch_result, content = -1, None
            else:
                fetch_result, content = 0, None

        return fetch_result, content

    def working(self, params, proxy):
        ksou_Header['User-Agent'] = make_random_useragent()

        tar_url = "http://www.ksouhouse.com/rp.php"
        ksou_params["q"] = params["Suburb"]
        ksou_params["region"] = params["Suburb"]
        ksou_params["sta"] = params["State"].lower()
        ksou_params["p"] = params["Index"]
        proxies = {
            "http": "http://" + proxy,
            "https": "http://" + proxy,
        }

        r = requests.get(tar_url, headers=ksou_Header, params=ksou_params, proxies=proxies, timeout=(6.05, 20))
        result = r.text

        if "Unauthorized" in result:
            return -1, None
        elif "Here is the address example" in result:
            return -2, None
        elif r.status_code == 200:
            return 1, result
        else:
            return -1, None


if __name__ == '__main__':
    pass
