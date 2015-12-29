#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from app.commons.base_service import BaseService
from app.daos.wexin_subscribe_dao import WeixinSubscribeDao, WeixinSubscribe
from app.services.bos.common import BoolRespBO
from configs.database_builder import DatabaseBuilder

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

    def subscribe(self, weixin_subscribe_req_bo):
        """ 关注公众账号

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
            if weixin_subscribe is None:
                weixin_subscribe = WeixinSubscribe()
                weixin_subscribe.weixin_num = weixin_num
                weixin_subscribe.open_id = open_id
                weixin_subscribe.is_subscribed = True
                weixin_subscribe_dao.add(weixin_subscribe)
            else:
                if not weixin_subscribe.is_subscribed:
                    weixin_subscribe.is_subscribed = True
                    weixin_subscribe_dao.update(weixin_subscribe)

    def unsubscribe(self, weixin_subscribe_req_bo):
        """

        :param weixin_subscribe_req_bo:
        :type weixin_subscribe_req_bo:
        :return:
        :rtype:
        """
        with self.create_session(self._default_db) as session:
            weixin_subscribe_dao = WeixinSubscribeDao(session)
            open_id = weixin_subscribe_req_bo.open_id
            weixin_num = weixin_subscribe_req_bo.weixin_num
            weixin_subscribe = weixin_subscribe_dao.get_by_weixin_num_open_id(weixin_num, open_id)
            if weixin_subscribe is None:
                weixin_subscribe = WeixinSubscribe()
                weixin_subscribe.weixin_num = weixin_num
                weixin_subscribe.open_id = open_id
                weixin_subscribe.is_subscribed = False
                weixin_subscribe_dao.add(weixin_subscribe)
            else:
                if weixin_subscribe.is_subscribed:
                    weixin_subscribe.is_subscribed = False
                    weixin_subscribe_dao.update(weixin_subscribe)

    def update_subscribe(self, weixin_num, open_id, is_subscribed):
        """

        :param weixin_num:
        :type weixin_num:
        :param open_id:
        :type open_id:
        :param is_subscribed:
        :type is_subscribed:
        :return:
        :rtype:
        """

        with self.create_session(self._default_db) as session:
            weixin_subscribe_dao = WeixinSubscribeDao(session)
            weixin_subscribe = weixin_subscribe_dao.get_by_weixin_num_open_id(weixin_num, open_id)
            if weixin_subscribe is None:
                weixin_subscribe = WeixinSubscribe()
                weixin_subscribe.weixin_num = weixin_num
                weixin_subscribe.open_id = open_id
                weixin_subscribe.is_subscribed = is_subscribed
                weixin_subscribe_dao.add(weixin_subscribe)
            else:
                weixin_subscribe.is_subscribed = is_subscribed
                weixin_subscribe_dao.update(weixin_subscribe)

