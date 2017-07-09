#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = 'AL'

import redis
import json
import configparser
from logger_config import report_logger

TASK_LIST = "idle_tasks"  # flag of idle_tasks
TASK_SET = "task_set"   # 任务集合
PROXY_SET = "proxy_set"  # 已经获取过的ip集合
PROXY_LIST = "proxy_pool"  # 当前可以ip集合


class RedisClient(object):
    def __init__(self):
        config = configparser.ConfigParser()
        config.read("../Config/config.ini")
        host = config.get("redis", "host")
        port = int(config.get("redis", "port"))
        pool = redis.ConnectionPool(host=host, port=port)
        self.client = redis.StrictRedis(connection_pool=pool)

    def flush_all(self):
        """初始化所有的key"""
        self.client.flushall()
        report_logger.error("Redis 擦除完成")

    def insert_proxy_set(self, proxy: str):
        """将不存在于代理集合中的IP,加入集合中,并插入可用代理列表的末尾"""
        if not self.client.sismember(PROXY_SET, proxy):
            self.client.sadd(PROXY_SET, proxy)
            self.client.rpush(PROXY_LIST, proxy)

    def add_proxy_list(self, ip: str):
        "将一个有效的代理插回队列中"
        self.client.rpush(PROXY_LIST, ip)

    def get_one_proxy(self):
        "获取一个代理,如果列表为空则阻塞"
        result = self.client.blpop(PROXY_LIST)
        result = result[1].decode()
        return result

    def proxy_list_size(self):
        "获取剩余代理数量"
        return self.client.llen(PROXY_LIST)

    def add_idle_task(self, *args, deep=0, repeat=0):
        """
        插入一个任务到redis爬取任务列表并返回当前列表长度
        args : suburb , sta , index 
        """
        suburb = args[0]
        state = args[1]
        index = args[2]
        task_item = {"Suburb": suburb, "State": state, "Index": index, "Deep": deep, "Repeat": repeat}
        self.client.rpush(TASK_LIST, json.dumps(task_item))

    def add_new_task(self, *args, deep=0, repeat=0):
        suburb = args[0]
        state = args[1]
        index = args[2]
        task_set = json.dumps([suburb, state, index])
        if not self.client.sismember(TASK_SET, task_set):
            self.client.sadd(TASK_SET, task_set)
            task_item = {"Suburb": suburb, "State": state, "Index": index, "Deep": deep, "Repeat": repeat}
            self.client.rpush(TASK_LIST, json.dumps(task_item))

    def get_idle_task(self, num=1):
        """
        获得指定数量的空闲任务，没有空闲任务则返回[],数量不足则返回已有的
        每获取一个空闲任务，则爬取任务接收数量+1
        :param num: 需求的任务数量
        :return: [[pid,keys],]
        """
        if self.client.llen(TASK_LIST) == 0:
            return []

        result = list()
        for i in range(num):
            item = self.client.lpop(TASK_LIST)
            if item is None:
                break
            result.append(json.loads(item.decode()))
        return result

    def get_idle_tasks_size(self):
        """获取空闲任务数量"""
        return self.client.llen(TASK_LIST)


if __name__ == '__main__':
    redis_client = RedisClient()
    redis_client.add_idle_task("suburb", "sta", 0)
    result = redis_client.get_idle_task(1)
    print('tasks', result)

    redis_client.flush_all()
