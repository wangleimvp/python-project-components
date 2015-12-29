#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from wechat.wechat_helper import WechatHelper
from service_bo.bos.participant import CheckInForWeiXinGetReqBO
from service_bo.bos.weixin import WeixinSubscribeReqBO, WeixinLocationReqBO
from service_bo.wechat_notice_service import WeChatNoticeService
from service_bo.weixin_location_service import WeixinLocationService
from service_bo.weixin_subscribe_service import WeixinSubscribeService

__author__ = 'freeway'

_COMMON_RESPONSE = u""


def text_process(wechat, message):
    """ 通过微信公众账号接受消息并回复消息

    :param wechat:
    :param message:
    :return:
    """
    return wechat.response_text(_COMMON_RESPONSE)


def image_process(wechat, message):
    """ 通过微信公众账号接受图片并回复消息

    :param wechat:
    :param message:
    :return:
    """
    return wechat.response_text(_COMMON_RESPONSE)


def scancode_waitmsg_process(wechat, message):
    """ 扫码接口

    :param wechat:
    :type wechat:
    :param message:
    :type message:
    :return:
    :rtype:
    """
    return wechat.response_text(u'code_info not found')


def location_process(wechat, message):
    """ 通过公众账号接受用户地理位置

    :param wechat:
    :param message:
    :return:
    """
    return u'success'


def location_select_process(wechat, message):
    """ 向公众账号发位置

    :param wechat:
    :param message:
    :return:
    """
    return u'success'


def subscribe_process(wechat, message):
    """ 订阅公众账号

    :param wechat:
    :type wechat: wechat_sdk.WechatBasic
    :param message:
    :type message:
    :return:
    :rtype:
    """
    return wechat.response_news("success")


def unsubscribe_process(wechat, message):
    """ 取消关注

    :param wechat:
    :param message:
    :return:
    """
    return u'success'


def scan_process(wechat, message):
    logging.info(message.__dict__)
    return u'success'


def click_process(wechat, message):
    logging.info("message key:{0}".format(message.key))
    if message.key == "help_stranger_coffee":
        news = []
        item = {
            'title': u"",
            'description': u"",
            'picurl': "",
            'url': ""
        }
        news.append(item)
        return wechat.response_news(news)
    else:
        return wechat.response_text(_COMMON_RESPONSE)


class WechatReceiveDispatcher(object):

    _dispatch_dict = {
        'text': text_process,
        'image': image_process,
        'scancode_waitmsg': scancode_waitmsg_process,
        'location': location_process,
        'subscribe': subscribe_process,
        'unsubscribe': unsubscribe_process,
        'scan': scan_process,
        'location_select': location_select_process,
        'click': click_process
    }

    @classmethod
    def process(cls, wechat):
        # 获得解析结果, message 为 WechatMessage 对象 (wechat_sdk.messages中定义)
        message = wechat.get_message()

        process = cls._dispatch_dict.get(message.type, None)
        if process is None:
            response = wechat.response_text(_COMMON_RESPONSE)
        else:
            response = process(wechat, message)
        return response
