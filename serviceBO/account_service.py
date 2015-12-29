#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 2014-11-07

@author: huwei
"""
import hashlib

from commons import stringutil
from serviceBO.base_service import BaseService
from datebase.account_dao import AccountDao
from serviceBO.bos.account import AccountBO
from datebase.database_builder import DatabaseBuilder

__author__ = 'freeway'


class AccountService(BaseService):
    # 多次输入用户名和密码失败后的锁定时间
    LOCKED_TIME = 3600 * 1000

    def __init__(self):
        self._default_db = DatabaseBuilder.get_default_db_instance()

    @staticmethod
    def _get_account(account_name, account_type, app_id, session):
        account_dao = AccountDao(session)
        return account_dao.get_by_name_account_type_app_id(account_name, account_type, app_id)

    @staticmethod
    def _encrypted_password(password, salt):
        """
         * 密码加密
         * @param string password 密码
         * @param string salt 混淆码
         * @return string 加密后的密码
        """
        return hashlib.md5(hashlib.md5(password).hexdigest() + salt).hexdigest()

    @staticmethod
    def _create_new_salt():
        """创建一个新的混淆码。

        :return: string 混淆码
        """
        return stringutil.random_string(5)

    @staticmethod
    def _get_account_name(country_code, mobile):
        return "-".join([country_code, mobile])

    def is_exist_account(self, account_name, account_type, app_id):
        with self.create_session(self._default_db) as session:
            return self._get_account(account_name, account_type, app_id, session) is not None

    def is_exist_mobile(self, country_code, mobile, account_type):
        return self.is_exist_account(self._get_account_name(country_code, mobile), account_type, '')

    def gets_by_account_type(self, get_by_account_type_req_bo):
        """ account type查找账号

        :param get_by_account_type_req_bo:
        :type get_by_account_type_req_bo:  app.services.bos.account.GetByUserIdAccountTypeReqBO
        :return:
        :rtype:
        """
        with self.create_session(self._default_db) as session:
            account_dao = AccountDao(session)
            accounts = account_dao.gets_by_account_type(get_by_account_type_req_bo.account_type,
                                                        get_by_account_type_req_bo.app_id)
            return [AccountBO(**account.fields) for account in accounts]


