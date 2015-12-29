#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from wechat_sdk import WechatBasic
import yaml
from wechat.wechat_opensdk import WechatOpenSDK

__author__ = 'freeway'


class WeChatBuilder(object):

    _wechat_config = None
    _clients = {}
    run_mode = None

    @classmethod
    def get_wechat_basic_by_name(cls, name, access_token=None, access_token_expires_at=None, jsapi_ticket=None,
            jsapi_ticket_expires_at=None):
        """

        :param name:
        :type name:
        :param access_token:
        :type access_token:
        :param access_token_expires_at:
        :type access_token_expires_at:
        :param jsapi_ticket:
        :type jsapi_ticket:
        :param jsapi_ticket_expires_at:
        :type jsapi_ticket_expires_at:
        :return:
        :rtype: wechat_sdk.WechatBasic
        """
        config = cls.get_config_by_name(name)
        return WechatBasic(
            token=config["token"],
            appid=config["appid"],
            appsecret=config["appsecret"],
            partnerid=config["partnerid"],
            partnerkey=config["partnerkey"],
            paysignkey=config["paysignkey"],
            access_token=access_token,
            access_token_expires_at=access_token_expires_at,
            jsapi_ticket=jsapi_ticket,
            jsapi_ticket_expires_at=jsapi_ticket_expires_at)

    @classmethod
    def get_config_by_name(cls, name):
        if cls._wechat_config is None:
            with file(os.path.join(os.getcwd(), 'wechat.yaml'), 'r') as file_stream:
                cls._wechat_config = yaml.load(file_stream).get(cls.run_mode)
        return cls._wechat_config[name]

    @classmethod
    def get_wechat_open_sdk(cls, name):
        """ 获取微信open sdk 对象

        :param name:
        :return: WechatOpenSDK
        """
        config = cls.get_config_by_name(name)
        appid = config.get("appid")
        secret = config.get("appsecret")
        return WechatOpenSDK(appid, secret)