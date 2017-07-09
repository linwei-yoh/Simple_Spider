#!/usr/bin/env python4
# -*- coding: utf-8 -*-
# __author__ = 'AL'

import requests
import requests.adapters
import configparser

from Mongo_Helper import MongoHelper
from Redis_Helper import RedisClient

from component.Spider import Spider as WebSpider
from component.Schedule import Schedule
from overwrite.Fetch_Worker import RpFetchWorker
from overwrite.Parse_Worker import RpPaeseWorker
from overwrite.Save_Worker import RpSaveWorker


def WebSpider_Start():
    # 持久化数据库
    mongo_client = MongoHelper()
    # 缓存数据库
    redis_client = RedisClient()
    redis_client.flush_all()

    task_list = mongo_client.get_valid_task()
    task_size = len(task_list)
    print("待处理task数量 : %s" % task_size)
    if task_size == 0:
        print("无需要处理的task")
        return

    config = configparser.ConfigParser()
    config.read("../Config/config.ini")

    max_retries = int(config.get("spider", "retry_times"))
    thread_num = int(config.get("spider", "thread_num"))
    parser_num = int(config.get("spider", "parser_num"))
    monitor_time = int(config.get("spider", "monitor_time"))
    start_time = config.get("spider", "fast_start")
    end_time = config.get("spider", "fast_end")
    fast_fcy = int(config.get("spider", "fast_fcy"))
    nor_fcy = int(config.get("spider", "nor_fcy"))
    fetch_interval = int(config.get("spider", "fetch_interval"))

    schedule = Schedule(start_time, end_time, fast_fcy, nor_fcy, fetch_interval)

    print("爬取开始:-----------------")
    with requests.Session() as session:
        session.mount('https://', requests.adapters.HTTPAdapter(pool_maxsize=thread_num))
        session.mount('http://', requests.adapters.HTTPAdapter(pool_maxsize=thread_num))

        # 配置组件
        fetch_worker = RpFetchWorker(session, max_repeat=max_retries)
        parse_worker = RpPaeseWorker()
        save_worker = RpSaveWorker(mongo_client)
        web_spider = WebSpider(fetch_worker, parse_worker, save_worker, schedule, redis_client)

        # 根据任务状态表 添加任务队列
        print("开始载入task:-----------------")

        p = redis_client.client.pipeline()
        for task in task_list:
            suburb, state, index = task
            redis_client.add_new_task(suburb, state, index)
        p.execute()
        print("载入task完成:-----------------")

        # fetcher_num 采集线程数
        web_spider.start_work_and_wait_done(fetcher_num=thread_num, parser_num=parser_num, monitor_time=monitor_time)
    print("爬取完成")


if __name__ == '__main__':
    WebSpider_Start()