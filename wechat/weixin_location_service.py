#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from service_bo.base_service import BaseService
from datebase.daos.account_dao import AccountDao
from datebase.daos.weixin_location_dao import WeixinLocationDao, WeixinLocation
from service_bo.bos.account import AccountType
from service_bo.bos.weixin import WeixinLocationRspBO
from datebase.database_builder import DatabaseBuilder

__author__ = 'wanglei'


class WeixinLocationService(BaseService):

    def __init__(self):
        self._default_db = DatabaseBuilder.get_default_db_instance()
        
    def save(self, weixin_location_req_bo):
        """ 保存微信位置

        :param weixin_location_req_bo: WeixinLocationReqBO
        :type weixin_location_req_bo: app.services.bos.weixin.WeixinLocationReqBO
        :return:
        :rtype:
        """
        with self.create_session(self._default_db) as session:
            account_dao = AccountDao(session)
            weixin_location_dao = WeixinLocationDao(session)
            open_id = weixin_location_req_bo.open_id
            # open_id
            account_name = open_id
            # 获取微信账号
            account = account_dao.get_by_name_account_type_app_id(account_name, AccountType.WEIXIN,
                                                                  app_id=weixin_location_req_bo.app_id)
            if account:
                weixin_location_req_bo.user_id = account.user_id
                weixin_location = WeixinLocation()
                weixin_location.update(weixin_location_req_bo.flat_attributes)
                weixin_location_dao.add(weixin_location)

    def get_by_user_id(self, weixin_location_get_req_bo):
        """ 根据用户获取微信位置

        :param weixin_location_get_req_bo: WeixinLocationGetReqBO
        :type weixin_location_get_req_bo: app.services.bos.weixin.WeixinLocationGetReqBO
        :return:
        :rtype:
        """
        with self.create_session(self._default_db) as session:
            weixin_location_dao = WeixinLocationDao(session)
            weixin_location = weixin_location_dao.get_by_user_id(weixin_location_get_req_bo.user_id)
            return WeixinLocationRspBO(**weixin_location.fields) if weixin_location else None

    def get_by_app_id_open_id(self, weixin_location_get_req_bo):
        """ 根据app_id, open_id获取微信位置

        :param weixin_location_get_req_bo:
        :type weixin_location_get_req_bo: app.services.bos.weixin.WeixinLocationGetReqBO
        :return:
        :rtype:
        """
        with self.create_session(self._default_db) as session:
            weixin_location_dao = WeixinLocationDao(session)
            weixin_location = weixin_location_dao.get_by_app_id_open_id(weixin_location_get_req_bo.app_id, weixin_location_get_req_bo.open_id)
            return WeixinLocationRspBO(**weixin_location.fields) if weixin_location else None

