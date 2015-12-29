#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datebase.wexin_subscribe_dao import WeixinSubscribeDao
from service_bo.common import BoolRespBO

from datebase.database_builder import DatabaseBuilder
from service_bo.base_service import BaseService

__author__ = 'freeway'


class WeixinSubscribeService(BaseService):

    def __init__(self):
        self._default_db = DatabaseBuilder.get_default_db_instance()

    def is_subscribed(self, weixin_subscribe_req_bo):
        """ 是否已经订阅

        :param weixin_subscribe_req_bo:
        :type weixin_subscribe_req_bo: app.services.bos.weixin.WeixinSubscribeReqBO
        :return:
        :rtype:
        """
        with self.create_session(self._default_db) as session:
            weixin_subscribe_dao = WeixinSubscribeDao(session)
            open_id = weixin_subscribe_req_bo.open_id
            weixin_num = weixin_subscribe_req_bo.weixin_num
            weixin_subscribe = weixin_subscribe_dao.get_by_weixin_num_open_id(weixin_num, open_id)
            bool_resp_bo = BoolRespBO()
            if weixin_subscribe is None:
                return bool_resp_bo
            bool_resp_bo.result = weixin_subscribe.is_subscribed
            return bool_resp_bo
