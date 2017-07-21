#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = 'AL'

import redis
import json
from logger_config import report_logger
from Config import config

TASK_LIST = "idle_tasks"  # flag of idle_tasks
TASK_SET = "task_set"  # 任务集合

class RedisClient(object):
    def __init__(self):
        redis_config = config.DB_config.get("redis", None)
        pool = redis.ConnectionPool(host=redis_config['host'], port=redis_config['port'], db=redis_config["db"])
        self.client = redis.StrictRedis(connection_pool=pool)

    def init_tables(self):
        """初始化所有的key"""
        self.client.delete(TASK_LIST)
        self.client.delete(TASK_SET)
        print("Redis 擦除完成")

    def add_proxy_list(self, ip: str):
        "将一个有效的代理插回队列中"
        self.client.rpush(config.free_ipproxy_table, ip)

    def get_one_proxy(self):
        "获取一个代理,如果列表为空则阻塞"
        *_, result = self.client.blpop(config.free_ipproxy_table)
        return result.decode()

    def proxy_list_size(self):
        "获取剩余代理数量"
        return self.client.llen(config.free_ipproxy_table)

    def add_idle_task(self, *args, deep=0, repeat=0):
        """
        不带去重的任务插入
        """
        suburb, state, postcode, index, key = args
        task_item = {"Suburb": suburb, "State": state, "Postcode": postcode, "Index": index, "Key": key,
                     "Deep": deep, "Repeat": repeat}
        self.client.rpush(TASK_LIST, json.dumps(task_item))

    def add_new_task(self, *args, deep=0, repeat=0):
        """带去重的任务插入"""
        suburb, state, postcode, index, key = args
        task_set = json.dumps(args)
        if not self.client.sismember(TASK_SET, task_set):
            self.client.sadd(TASK_SET, task_set)
            task_item = {"Suburb": suburb, "State": state, "Postcode": postcode, "Index": index, "Key": key,
                         "Deep": deep, "Repeat": repeat}
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

    redis_client.init_tables()
