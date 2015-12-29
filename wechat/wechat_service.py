#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datebase.weixin_app_context_dao import WeixinAppContextDao
from service_bo.bos.weixin import WeixinAppContextBO

from datebase.database_builder import DatabaseBuilder
from memcache.memcache_factory import cache_get
from service_bo.base_service import BaseService

__author__ = 'freeway'


class WeChatService(BaseService):
    def __init__(self):
        self._default_db = DatabaseBuilder.get_default_db_instance()

    @cache_get(session='default', name='wxapp')
    def get_by_app_id(self, app_id):
        """

        :param app_id:
        :type app_id:
        :return:
        :rtype: app.services.bos.weixin.WeixinAppContextBO
        """
        with self.create_session(self._default_db) as session:
            weixin_app_context_dao = WeixinAppContextDao(session)
            weixin_app_context = weixin_app_context_dao.get_by_app_id(app_id)
            if weixin_app_context is None:
                return None
            else:
                return WeixinAppContextBO(**weixin_app_context.fields)
