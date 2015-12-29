#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import deque
import string
import random
from sqlalchemy import exc
from commons import stringutil
from datebase.database_builder import DatabaseBuilder

__author__ = 'freeway'


class DatabaseSequenceFactory(object):
    """ 所有Dao对象需要集成DatabaseTemplate
    """
    sequences = dict()  # 缓存系统中所有的id

    def __init__(self, database_factory=None, alphabet=None):
        self._default_db = DatabaseBuilder.get_default_db_instance() if database_factory is None else database_factory
        self.alphabet = "wWBLCMPZbH2GFszTogYu93JNDfIlVmneRx6tkAvKU51r8XOidpchEjQqS7a40y" if alphabet is None else alphabet

    def get_id(self, name_space, name):  # 默认为当前项目的name_space 具体项目要修改这个默认值
        sequence_key = "%r:%r" % (name_space, name)
        sequence = self.sequences.get(sequence_key)
        if sequence is None or len(sequence) == 0:
            # id消费完了,重新获取一组
            start_id, step = self._get_start_id_step(name_space, name)
            sequence = deque(range(start_id, start_id+step))
            self.sequences[sequence_key] = sequence

        return sequence.popleft()

    def get_obfuscated_id(self, name_space, name, alphabet=None, has_random=False, random_length=1, is_prefix=True):
        result = stringutil.base62_encode(self.get_id(name_space, name),
                                          alphabet if alphabet is not None else self.alphabet)
        if has_random:
            random_str = ''.join(random.sample(string.ascii_letters+string.digits, random_length))
            result = random_str+'_'+result if is_prefix else result+'_'+random_str
        return result

    def _get_start_id_step(self, name_space, name):
        """

        :param name_space:
        :param name:
        :return: tupple (start_id, step)
        """

        with self._default_db.create_connection() as connection:
            update_sql = "update sequences set next_id = last_insert_id(next_id+step) where name=%s and name_space=%s"
            select_sql = "select last_insert_id()-step as start_id, step from sequences " +\
                         "where name=%s and name_space=%s"
            result = connection.execute(update_sql, name, name_space)
            if result.rowcount == 0:
                raise exc.ArgumentError("sequence is not exist namespace:%r name:%r" % (name_space, name))
            entity = connection.execute(select_sql, name, name_space).first()
            return entity[0], entity[1]


if __name__ == "__main__":
    DatabaseBuilder.run_mode = 'test'
    for i in range(0, 100000):

        print DatabaseSequenceFactory().get_id('aiwanr','hehe')
        # print DatabaseSequenceFactory().get_obfuscated_id('aiwanr','users')
        # print DatabaseSequenceFactory().get_obfuscated_id('aiwanr','users', has_random=True)
        # print DatabaseSequenceFactory().get_obfuscated_id('aiwanr','users', has_random=True,
        #                                                   random_length=2, is_prefix=False)