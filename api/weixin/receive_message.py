#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from tornado.web import RequestHandler
from api.weixin.receive_dispatcher import WechatReceiveDispatcher
from wechat.wechat_helper import WechatHelper

__author__ = 'freeway'


class WeChatReceiveMessageHandler(RequestHandler):
    """微信回调接口

    """

    def check_xsrf_cookie(self):
        """ 忽略 xsrf 检查

        :return:
        """
        pass

    def get(self, *args, **kwargs):
        """ for check api is valid

        :param args:
        :param kwargs:
        :return:
        """
        signature = self.get_argument("signature", None)
        timestamp = self.get_argument("timestamp", None)
        nonce = self.get_argument("nonce", None)
        echostr = self.get_argument("echostr", None)

        # 实例化 wechat
        wechat = WechatHelper.get_wechat_basic()
        # 对签名进行校验
        if wechat.check_signature(signature=signature, timestamp=timestamp, nonce=nonce):
            self.write(echostr)
        else:
            self.write("signature is invalid")

    def post(self, *args, **kwargs):
        """ 接收从微信公众账号收到的消息

        :param args:
        :param kwargs:
        :return:
        """
        signature = self.get_argument("signature", None)
        timestamp = self.get_argument("timestamp", None)
        nonce = self.get_argument("nonce", None)
        # 实例化 wechat
        wechat = WechatHelper.get_wechat_basic()
        # 对签名进行校验
        if wechat.check_signature(signature=signature, timestamp=timestamp, nonce=nonce):

            # 对 XML 数据进行解析 (必要, 否则不可执行 response_text, response_image 等操作)
            logging.info(self.request.body)
            wechat.parse_data(self.request.body)
            # 获得解析结果, message 为 WechatMessage 对象 (wechat_sdk.messages中定义)
            response = WechatReceiveDispatcher.process(wechat)
        else:
            response = wechat.response_text(u'')
        self.write(response)
