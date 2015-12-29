#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from datebase.participant_order_dao import ParticipantOrderDao
from datebase.participant_refund_dao import ParticipantRefundDao
from datebase.weixin_app_context_dao import WeixinAppContextDao, WeixinAppContext
from datebase.weixin_refund_result_dao import WeixinRefundResultDao, WeixinRefundResult
from datebase.weixin_unifiedorder_result_dao import WeixinUnifiedorderResultDao, WeixinUnifiedorderResult
from service_bo.bos.weixin import WeixinAppContextBO

from commons import stringutil
from datebase.database_builder import DatabaseBuilder
from memcache.memcache_factory import cache_get, cache_set
from service_bo.base_service import BaseService, ServiceException
from wechat.wechat_builder import WeChatBuilder
from wechat.wxpay import WxPayApi

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

    @cache_set(session='default', name='wxapp', key_attr='app_id')
    def save(self, wexin_app_context_bo):
        with self.create_session(self._default_db) as session:
            weixin_app_context_dao = WeixinAppContextDao(session)
            weixin_app_context = weixin_app_context_dao.get_by_app_id(wexin_app_context_bo.app_id)
            if weixin_app_context is None:
                weixin_app_context = WeixinAppContext()
                weixin_app_context.app_id = wexin_app_context_bo.app_id
                weixin_app_context.access_token = wexin_app_context_bo.access_token
                weixin_app_context.jsapi_ticket = wexin_app_context_bo.jsapi_ticket
                weixin_app_context.expires_at = wexin_app_context_bo.expires_at
                weixin_app_context.jsapi_ticket_expires_at = wexin_app_context_bo.jsapi_ticket_expires_at
                weixin_app_context_dao.add(weixin_app_context)
            else:
                weixin_app_context.access_token = wexin_app_context_bo.access_token
                weixin_app_context.jsapi_ticket = wexin_app_context_bo.jsapi_ticket
                weixin_app_context.expires_at = wexin_app_context_bo.expires_at
                weixin_app_context.jsapi_ticket_expires_at = wexin_app_context_bo.jsapi_ticket_expires_at
                weixin_app_context_dao.update(weixin_app_context)

    def unified_order(self, remote_address, wx_pay_unified_order):
        """
        微信统一下单，保存下单结果
        :param wx_prepay_req_bo:
        :return: 下单结果
        """
        wechat_config = WeChatBuilder.get_config_by_name('pay')
        app_id = wechat_config.get('app_id', None)
        mch_id = wechat_config.get('mch_id', None)
        key = wechat_config.get('key', None)
        app_secret = wechat_config.get('app_secret', None)
        notify_url = wechat_config.get('notify_url', None)
        wx_api = WxPayApi(app_id, mch_id, key, app_secret, notify_url, remote_address, report_levenl=0)
        wx_result = wx_api.unified_order(wx_pay_unified_order)
        wx_result_dict = wx_result.get_values()
        logging.info(wx_result_dict)
        if wx_result_dict['return_code'] == 'SUCCESS' and wx_result_dict['result_code'] == 'SUCCESS':
            # TODO 验证结果?
            with self.create_session(self._default_db) as session:
                wur_dao = WeixinUnifiedorderResultDao(session)
                wur = WeixinUnifiedorderResult()
                wur.update(wx_result_dict)
                instance = wur_dao.add(wur)
                # 更新订单和微信结果关联
                # TODO 这里有问题，没有关联上
                order_dao = ParticipantOrderDao(session)
                order = order_dao.get_by_order_id(wx_pay_unified_order.out_trade_no)
                order.third_party_results_id = instance.result_id
                order_dao.update(order)
            return wx_result_dict
        else:
            raise ServiceException(20401, 'unified order failed')

    def refund(self, remote_address, wx_pay_refund, cert):

        """
        微信退款
        :param remote_address:
        :param wx_pay_refund:
        """
        wechat_config = WeChatBuilder.get_config_by_name('pay')
        app_id = wechat_config.get('app_id', None)
        mch_id = wechat_config.get('mch_id', None)
        key = wechat_config.get('key', None)
        app_secret = wechat_config.get('app_secret', None)
        notify_url = wechat_config.get('notify_url', None)
        wx_api = WxPayApi(app_id, mch_id, key, app_secret, notify_url, remote_address, report_levenl=0)
        wx_result = wx_api.refund(wx_pay_refund, cert=cert)
        wx_result_dict = wx_result.get_values()
        logging.info(wx_result_dict)
        if wx_result_dict['return_code'] == 'SUCCESS' and wx_result_dict['result_code'] == 'SUCCESS':
            # TODO 验证结果?
            with self.create_session(self._default_db) as session:
                wxrr_dao = WeixinRefundResultDao(session)
                wxrr = WeixinRefundResult()
                wxrr.update(wx_result_dict)
                instance = wxrr_dao.add(wxrr)
                # 更新退款和微信结果关联
                participant_refund_dao = ParticipantRefundDao(session)
                participant_refund = participant_refund_dao.get_by_order_id(wx_pay_refund.out_trade_no)
                participant_refund.third_party_results_id = instance.result_id
                participant_refund_dao.update(participant_refund)
            return wx_result_dict
        else:
            raise ServiceException(20405, 'refund failed')

    @staticmethod
    def get_wx_js_api_params(prepay_id):
        # 获取微信配置
        wechat_config = WeChatBuilder.get_config_by_name('pay')
        app_id = wechat_config.get('app_id', None)
        key = wechat_config.get('key', None)
        # 生成签名
        nonce_str = WxPayApi.gen_noce_str()
        time_stamp = WxPayApi.timestamp()
        package = 'prepay_id=' + prepay_id
        sign_type = 'MD5'
        data = {
            'appId': app_id,
            'nonceStr': nonce_str,
            'package': package,
            'signType': sign_type,
            'timeStamp': time_stamp
        }
        keys = data.keys()
        keys.sort()
        data_str = '&'.join(['%s=%s' % (k, data[k]) for k in keys])
        data_str += '&key=' + key
        logging.info(data_str)
        pay_sign = stringutil.md5(data_str).upper()
        result = dict(
            app_id=app_id,
            time_stamp=time_stamp,  # 当前的时间,单位秒
            nonce_str=nonce_str,
            package=package,
            sign_type=sign_type,
            pay_sign=pay_sign
        )
        return result
