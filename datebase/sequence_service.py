#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
from service_bo.base_service import BaseService

from datebase.database_builder import DatabaseBuilder


class SequenceService(BaseService):
    """用户数据访问对象"""
    sequences = dict()  # 缓存系统中所有的id

    def __init__(self):
        self._default_db = DatabaseBuilder.get_default_db_instance()

    def get_id(self, name, name_space=''):  # 默认为当前项目的name_space 具体项目要修改这个默认值
        if name_space + ":" + name in self.sequences:
            # 缓存中存在
            sequence = self.sequences[name_space + ":" + name]
            ids = sequence["ids"]
            if len(ids) <= 0:
                # id消费完了,重新获取一组
                step = sequence["step"]
                last_id = self.get_last_id(name, name_space)
                ids = range(last_id - step, last_id)
                sequence["ids"] = ids
        else:
            # 缓存中不存在 从数据库中获取step和ids
            step = self.get_step(name, name_space)
            last_id = self.get_last_id(name, name_space)
            ids = range(last_id - step, last_id)
            self.sequences[name_space + ":" + name] = dict(step=step,
                                                           ids=ids)
        return ids.pop(0)

    def get_step(self, name, name_space):
        with self.create_session(self._default_db) as session:
            sql = "select step from sequences where name = :name and name_space= :name_space; "
            params = dict(name=name,
                          name_space=name_space)
            entities = session.execute(sql, params)
            return entities.first()[0]

    def get_last_id(self, name, name_space):
        with self.create_session(self._default_db) as session:
            sql1 = "update sequences set next_id = last_insert_id(next_id+step) where name = :name and name_space= :name_space"
            params = dict(name=name,
                          name_space=name_space)
            sql2 = "select last_insert_id()"
            session.execute(sql1, params)
            entities = session.execute(sql2, params)
            return entities.first()[0]

    @staticmethod
    def convert_to_36(val, encryption=False):
        """

        :param val: 要转换的10进制数字
        :param encryption:是否混淆(加密)
        :return:
        """
        base_code = list("0123456789abcdefghijklmnopqrstuvwxyz")
        if encryption:
            base_code = list("prq1x5szdgwcon87v3ya4lbiek2hu69fmt0j")
        result = ""
        while val >= 36:
            result = base_code[val % 36] + result
            val /= 36

        if val >= 0:
            result = base_code[val] + result
        return result
