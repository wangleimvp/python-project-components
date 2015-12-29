#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column, BigInteger, String, Integer

from database import BaseModel, DatabaseTemplate, model
from database_mixin import IdMixin, CreatedAtMixin, UpdatedAtMixin


__author__ = 'freeway'


class AccountStatus(object):
    SEND_CODE = 'send_code'
    INPUT_PASSWORD = 'input_password'
    INPUT_REAL_PROFILE = 'input_real_profile'


class Account(IdMixin, CreatedAtMixin, UpdatedAtMixin, BaseModel):
    # 用户id
    user_id = Column(BigInteger, default=0L)
    # 账号类型
    account_type = Column(String(10), default=None)
    # 应用id
    app_id = Column(String(32))
    # 账号名称
    name = Column(String(80), default=None)
    # 最后一次访问成功的ip
    last_visit_ip = Column(String(50), default=None)
    # 最后一次登录的ip
    last_login_ip = Column(String(50), default=None)
    # 连续登录失败次数
    fail_count = Column(Integer, default=0L)
    # 锁定的时间，预计1-2小时候解锁
    locked_at = Column(BigInteger, default=0L)


@model(Account)
class AccountDao(DatabaseTemplate):

    def get_by_name_account_type_app_id(self, name, account_type, app_id=''):
        """

        :param account:
        :param account_type:
        :return:
        """
        return self.get_first_by_criterion(Account.name == name,
                                           Account.account_type == account_type,
                                           Account.app_id == app_id)

    def get_by_user_id_account_type(self, user_id, account_type, app_id=''):
        """ 根据用户id和账号类型获取账号

        :param user_id: 用户id
        :param account_type: 账号类型
        :param app_id:
        :return:
        """
        return self.get_first_by_criterion(Account.user_id == user_id,
                                           Account.account_type == account_type,
                                           Account.app_id == app_id)

    def gets_by_account_type(self, account_type, app_id=''):
        """ 根据账号类型获取账号

        :param account_type:
        :type account_type:
        :param app_id:
        :type app_id:
        :return:
        :rtype:
        """
        return self.session.query(self.model_cls).filter(Account.account_type == account_type,
                                                         Account.app_id == app_id).all()