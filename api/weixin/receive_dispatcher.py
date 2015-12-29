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
    return wechat.response_text(_COMMON_RESPONSE)


def image_process(wechat, message):
    return wechat.response_text(_COMMON_RESPONSE)


def scancode_waitmsg_process(wechat, message):
    """

    :param wechat:
    :type wechat:
    :param message:
    :type message:
    :return:
    :rtype:
    """
    # logging.info(message.__dict__)
    code_info = message.ScanCodeInfo
    if code_info:
        scan_result = code_info[0].get("ScanResult", None)
        scan_type = code_info[0].get("ScanType", None)
        if scan_type == 'qrcode':
            if message.key == 'scancode_checkin':
                logging.info("ScanResult:{0}".format(scan_result))
                wechat_notice_service = WeChatNoticeService()
                check_in_for_weixin_get_req_bo = CheckInForWeiXinGetReqBO()
                check_in_for_weixin_get_req_bo.app_id = WechatHelper.get_app_id()
                check_in_for_weixin_get_req_bo.open_id = message.source
                check_in_for_weixin_get_req_bo.paty_id_checkin_code = scan_result
                result = wechat_notice_service.check_in_for_weixin(check_in_for_weixin_get_req_bo)
                return wechat.response_text(result)
    return wechat.response_text(u'code_info not found')


def location_process(wechat, message):
    logging.info("latitude:{0} longitude:{1} precision:{2}".format(message.latitude,
                                                                   message.longitude,
                                                                   message.precision))
    weixin_location_service = WeixinLocationService()
    weixin_location_req_bo = WeixinLocationReqBO()
    weixin_location_req_bo.app_id = WechatHelper.get_app_id()
    weixin_location_req_bo.open_id = message.source
    weixin_location_req_bo.latitude = message.latitude
    weixin_location_req_bo.longitude = message.longitude
    weixin_location_service.save(weixin_location_req_bo)
    return u'success'


def location_select_process(wechat, message):
    location_info = message.SendLocationInfo
    # if location_info:
    #     print(location_info)
    return u'success'


def subscribe_process(wechat, message):
    """

    :param wechat:
    :type wechat: wechat_sdk.WechatBasic
    :param message:
    :type message:
    :return:
    :rtype:
    """
    weixin_subscribe_service = WeixinSubscribeService()
    weixin_subscribe_req_bo = WeixinSubscribeReqBO()
    weixin_subscribe_req_bo.weixin_num = message.target
    weixin_subscribe_req_bo.open_id = message.source
    weixin_subscribe_service.subscribe(weixin_subscribe_req_bo)
    news = []
    item = {
        'title': u"",
        'description': u"",
        'picurl': "",
        'url': ""
    }
    news.append(item)
    return wechat.response_news(news)


def unsubscribe_process(wechat, message):
    weixin_subscribe_service = WeixinSubscribeService()
    weixin_subscribe_req_bo = WeixinSubscribeReqBO()
    weixin_subscribe_req_bo.weixin_num = message.target
    weixin_subscribe_req_bo.open_id = message.source
    weixin_subscribe_service.unsubscribe(weixin_subscribe_req_bo)
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
