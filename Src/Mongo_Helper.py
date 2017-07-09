#!/usr/bin/env python4
# -*- coding: utf-8 -*-
# __author__ = 'AL'

from pymongo import MongoClient
import pymongo.errors
import pymongo
import configparser

from component.logger_config import report_logger as logger

data_base = 'ksou_db'
page_table = 'ksou_detail'
task_table = 'ksou_task_record'


class MongoHelper(object):
    def __init__(self):
        config = configparser.ConfigParser()
        config.read("../Config/config.ini")
        host = config.get("mongo", "host")
        port = config.get("mongo", "port")
        self.client = MongoClient(host, int(port))
        self.database = self.client[data_base]
        self.detail_table = self.database[page_table]
        self.task_table = self.database[task_table]
        self.create_index()

    def recreate(self):
        """
        慎用！ 删除一个数据库的内容，重新建立表和索引  慎用！
        :return: T/F
        """
        self.client.drop_database(data_base)
        return self.create_index()

    def create_index(self):
        """
        建立唯一索引索引 
        :return: T/F
        """
        # 对一个表建立 复合 唯一索引，且在后台执行
        # dropDups在3.0和之后的mongodb中不再被支持，遇到重复文档则会报错
        self.database = self.client[data_base]
        self.detail_table = self.database[page_table]
        self.task_table = self.database[task_table]
        try:
            self.detail_table.create_index([("Rid", pymongo.ASCENDING)],background=True)
            self.task_table.create_index([("Suburb", pymongo.ASCENDING), ("State", pymongo.ASCENDING),
                                          ("Index", pymongo.ASCENDING)],
                                         unique=True, background=True)
        except pymongo.errors.DuplicateKeyError:
            print("创建索引失败，已存在重复数据")
            logger.error("创建索引失败")
            return False
        except Exception:
            return False
        return True

    def insert_tasks(self, pid_items: list):
        """
        插入任务队列
        :param pid_items: [(suburb,state),]
        :return: 
        """
        try:
            tasks = [{"Suburb": suburb, "State": state, "indexes": []} for suburb, state, *_ in pid_items]
            self.task_table.insert_many(tasks, ordered=False)

        except (IndexError, ValueError) as e:
            logger.error(e)
        except Exception as e:
            logger.warning(e)

    def reset_task_record(self):
        try:
            self.task_table.update_many({}, {"$set": {"indexes": []}})
            return True
        except Exception:
            logger.error("重置task状态失败")
            return False

    def update_task_record(self, Suburb: str, State: str, Index):
        """
        更新task记录状态
        :param Suburb:  
        :param State: 
        :param Index: 页面序号
        :return: 
        """
        State = State.upper()
        try:
            self.task_table.update_one({"Suburb": str(Suburb), "State": str(State)},
                                       {"$addToSet": {"indexes": Index}})
        except Exception as e:
            logger.error("更新任务记录失败 id : "+ str(e))

    def get_valid_task(self, limit: int = 0):
        """
        获得还有未完成d的任务
        :return: 包含所有未执行的任务
        """
        cursor = self.task_table.find({"indexes": {"$nin": [False]}, "indexes.30": {"$exists": 0}},
                                      {"_id": 0, "Suburb": 1, "State": 1, "indexes": 1}).limit(limit)

        task_list = list()
        for task in cursor:
            suburb = task["Suburb"]
            state = task["State"]
            if len(task["indexes"]) == 0:
                task_list.append([suburb, state, 0])
            else:
                for i in range(30):
                    if i not in task["indexes"]:
                        task_list.append([suburb, state, i])

        return task_list

    def delete_task_record(self):
        """
        清空任务记录表中的内容
        :return: 
        """
        self.task_table.delete_many({})

    def insert_detail_page(self, content: dict):
        """
        插入一个新的记录
        :param content: [{'a':1}]
        :return: 
        """
        try:
            self.detail_table.insert_one(content)
            return True
        except Exception as e:
            logger.error("insert detail page faile " + str(e))
            return False

    def check_index(self):
        for i in self.task_table.list_indexes():
            print(i)

    def check_size(self):
        print("任务表数量", self.task_table.count())
        print("页面表数量", self.detail_table.count())

    def get_task_record(self, suburb, state):
        cursor = self.task_table.find({"Suburb": suburb, "State": state},
                                      {"_id": 0, "Suburb": 1, "State": 1, "indexes": 1})
        result = []
        for task in cursor:
            result.append(task)
        return result


if __name__ == '__main__':
    # 慎用
    MongoDB = MongoHelper()
    MongoDB.insert_tasks([['Goulburn', 'NSW']])
    resutlt = MongoDB.update_task_record("Goulburn", "NSW",1)
    MongoDB.recreate()

