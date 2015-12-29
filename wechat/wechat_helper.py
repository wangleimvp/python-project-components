#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from service_bo.bos.weixin import WeixinAppContextBO
from service_bo.wechat_service import WeChatService
from wechat.wechat_builder import WeChatBuilder

__author__ = 'freeway'


class WechatHelper(object):

    @staticmethod
    def get_wechat_basic():
        """ 获取wechat对象

        :return:
        :rtype: wechat_sdk.WechatBasic
        """
        config = WeChatBuilder.get_config_by_name('default')
        app_id = config.get('appid')
        wechat_service = WeChatService()
        weixin_app_context = wechat_service.get_by_app_id(app_id)
        if weixin_app_context:
            wechat = WeChatBuilder\
                .get_wechat_basic_by_name('default',
                                          access_token=weixin_app_context.access_token,
                                          access_token_expires_at=weixin_app_context.expires_at/1000,
                                          jsapi_ticket=weixin_app_context.jsapi_ticket,
                                          jsapi_ticket_expires_at=weixin_app_context.jsapi_ticket_expires_at/1000)

        else:
            wechat = WeChatBuilder.get_wechat_basic_by_name('default')

        access_token_dict = wechat.get_access_token()
        jsapi_ticket_dict = wechat.get_jsapi_ticket()
        new_access_token = access_token_dict.get("access_token")
        new_jsapi_ticket = jsapi_ticket_dict.get("jsapi_ticket")
        if weixin_app_context:
            if weixin_app_context.access_token != new_access_token\
                    or weixin_app_context.jsapi_ticket != new_jsapi_ticket:

                weixin_app_context.access_token = new_access_token
                weixin_app_context.jsapi_ticket = new_jsapi_ticket
                weixin_app_context.expires_at = long(access_token_dict.get("access_token_expires_at")*1000)
                weixin_app_context.jsapi_ticket_expires_at = long(jsapi_ticket_dict.get("jsapi_ticket_expires_at")*1000)
        else:
            weixin_app_context = WeixinAppContextBO()
            weixin_app_context.app_id = app_id
            weixin_app_context.access_token = new_access_token
            weixin_app_context.jsapi_ticket = new_jsapi_ticket
            weixin_app_context.expires_at = long(access_token_dict.get("access_token_expires_at")*1000)
            weixin_app_context.jsapi_ticket_expires_at = long(jsapi_ticket_dict.get("jsapi_ticket_expires_at")*1000)
        wechat_service.save(weixin_app_context)

        return wechat

    @classmethod
    def generate_jsapi_signature(cls, timestamp, noncestr, url):
        wechat_basic = cls.get_wechat_basic()
        jsapi_ticket_dict = wechat_basic.get_jsapi_ticket()
        logging.info(jsapi_ticket_dict.get("jsapi_ticket"))
        return wechat_basic.generate_jsapi_signature(timestamp, noncestr, url, jsapi_ticket_dict.get("jsapi_ticket"))

    @staticmethod
    def get_app_id(name='default'):
        config = WeChatBuilder.get_config_by_name(name)
        return config.get('appid', None)

    @staticmethod
    def get_weixin_num(name='default'):
        config = WeChatBuilder.get_config_by_name(name)
        return config.get('weixin_num', None)

    @classmethod
    def get_access_token(cls):
        """ 获取应用的access token

        :return:
        """
        wechat_basic = cls.get_wechat_basic()
        access_token_dict = wechat_basic.get_access_token()
        return access_token_dict.get("access_token")
