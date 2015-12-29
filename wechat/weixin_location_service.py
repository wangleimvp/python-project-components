#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datebase.weixin_location_dao import WeixinLocationDao
from service_bo.bos.weixin import WeixinLocationRspBO

from datebase.database_builder import DatabaseBuilder
from service_bo.base_service import BaseService

__author__ = 'wanglei'


class WeixinLocationService(BaseService):

    def __init__(self):
        self._default_db = DatabaseBuilder.get_default_db_instance()

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