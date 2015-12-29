#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib
import logging
import os
import random
import string
import time
import datetime
import requests
from wechat_sdk.lib import XMLStore
from wechat.wxpay.exceptions import WxPayError
from wechat.wxpay.models import WxPayResults, WxPayUnifiedOrder, WxPayReport


class WxPayApi(object):
    def __init__(self, app_id, mch_id, key, app_secret, notify_url, remote_address, report_levenl=0):
        self.__app_id = app_id
        self.__mch_id = mch_id
        self.__key = key
        self.__app_secret = app_secret
        self.__notify_url = notify_url
        self.__remote_address = remote_address
        self.__report_levenl = report_levenl

    @staticmethod
    def gen_noce_str(length=32):
        return ''.join(random.sample(string.ascii_lowercase + string.digits, length))

    @staticmethod
    def timestamp(date_time=None):
        if date_time is None:
            date_time = datetime.datetime.now()
        return long(time.mktime(date_time.timetuple())) * 1000 + date_time.microsecond / 1000

    def unified_order(self, wx_pay_unified_order, timeout=6):
        """
        统一下单，WxPayUnifiedOrder中out_trade_no、body、total_fee、trade_type必填
        :param wx_pay_unified_order:
        :type wx_pay_unified_order: app.commons.wxpay.models.WxPayUnifiedOrder
        :param timeout:
        :type timeout:
        :return:
        :rtype:
        """
        url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
        # 检测必填参数
        if not wx_pay_unified_order.is_out_trade_no_set():
            raise WxPayError(u"缺少统一支付接口必填参数out_trade_no！")
        elif not wx_pay_unified_order.is_body_set():
            raise WxPayError(u"缺少统一支付接口必填参数body！")
        elif not wx_pay_unified_order.is_total_fee_set():
            raise WxPayError(u"缺少统一支付接口必填参数total_fee！")
        elif not wx_pay_unified_order.is_trade_type_set():
            raise WxPayError(u"缺少统一支付接口必填参数trade_type！")

        # 关联参数
        if wx_pay_unified_order.trade_type == "JSAPI" and (not wx_pay_unified_order.is_openid_set()):
            raise WxPayError(u"统一支付接口中，缺少必填参数openid！trade_type为JSAPI时，openid为必填参数！")
        if wx_pay_unified_order.trade_type == "NATIVE" and (not wx_pay_unified_order.is_product_id_set()):
            raise WxPayError(u"统一支付接口中，缺少必填参数product_id！trade_type为JSAPI时，product_id为必填参数！")

        # 异步通知url未设置，则使用配置文件中的url
        if not wx_pay_unified_order.is_notify_url_set():
            wx_pay_unified_order.notify_url = self.__notify_url

        wx_pay_unified_order.spbill_create_ip = self.__remote_address

        return self.post_model(url, wx_pay_unified_order, timeout)

    def order_query(self, input_obj, timeout=6):
        """
        查询订单，WxPayOrderQuery中out_trade_no、transaction_id至少填一个
        :param input_obj:
        :type input_obj: app.commons.wxpay.models.WxPayOrderQuery
        :param timeout:
        :type timeout:
        :return: 成功时返回，其他抛异常
        :rtype:
        :raise: WxPayError
        """
        url = "https://api.mch.weixin.qq.com/pay/orderquery"
        if (not input_obj.is_out_trade_no_set()) and (not input_obj.is_transaction_id_set()):
            raise WxPayError(u"订单查询接口中，out_trade_no、transaction_id至少填一个！")

        return self.post_model(url, input_obj, timeout)

    def close_order(self, input_obj, timeout=6):
        """
        关闭订单
        WxPayCloseOrder中out_trade_no必填，appid、mchid、spbill_create_ip、nonce_str不需要填入
        :param input_obj: WxPayCloseOrder
        :type input_obj: app.commons.wxpay.models.WxPayCloseOrder
        :param timeout:
        :type timeout:
        :return:
        :rtype:
        """
        url = "https://api.mch.weixin.qq.com/pay/closeorder"
        # 检测必填参数
        if not input_obj.is_out_trade_no_set():
            raise WxPayError(u"订单查询接口中，out_trade_no必填！")

        return self.post_model(url, input_obj, timeout)

    def refund(self, input_obj, timeout=6, cert=False):
        """
        申请退款，WxPayRefund中out_trade_no、transaction_id至少填一个且
        out_refund_no、total_fee、refund_fee、op_user_id为必填参数
        appid、mchid、spbill_create_ip、nonce_str不需要填入
        :param input_obj:  WxPayRefund
        :type input_obj: app.commons.wxpay.models.WxPayRefund
        :param timeout:
        :type timeout:
        :return:
        :rtype:
        """
        url = "https://api.mch.weixin.qq.com/secapi/pay/refund"
        if (not input_obj.is_out_trade_no_set()) and (not input_obj.is_transaction_id_set()):
            raise WxPayError(u"订单查询接口中，out_trade_no、transaction_id至少填一个！")
        elif not input_obj.is_out_refund_no_set():
            raise WxPayError(u"退款申请接口中，缺少必填参数out_refund_no！")
        elif not input_obj.is_total_fee_set():
            raise WxPayError(u"退款申请接口中，缺少必填参数total_fee！")
        elif not input_obj.is_refund_fee_set():
            raise WxPayError(u"退款申请接口中，缺少必填参数refund_fee！")
        elif not input_obj.is_op_user_id_set():
            raise WxPayError(u"退款申请接口中，缺少必填参数op_user_id！")
        elif not cert:
            raise WxPayError(u"缺少证书！")
        return self.post_model(url, input_obj, timeout, cert)

    def refund_query(self, input_obj, timeout=6):
        """
        查询退款
        提交退款申请后，通过调用该接口查询退款状态。退款有一定延时，
        用零钱支付的退款20分钟内到账，银行卡支付的退款3个工作日后重新查询退款状态。
        WxPayRefundQuery中out_refund_no、out_trade_no、transaction_id、refund_id四个参数必填一个
        appid、mchid、spbill_create_ip、nonce_str不需要填入
        :param input_obj: WxPayRefundQuery
        :type input_obj: app.commons.wxpay.models.WxPayRefundQuery
        :param timeout:
        :type timeout: int
        :return:
        :rtype:
        """
        url = "https://api.mch.weixin.qq.com/pay/refundquery"
        # 检测必填参数
        if (not input_obj.is_out_refund_no_set()) and \
                (not input_obj.is_out_trade_no_set()) and \
                (not input_obj.is_transaction_id_set()) and \
                (not input_obj.is_refund_id_set()):
            raise WxPayError(u"退款查询接口中，out_refund_no、out_trade_no、transaction_id、refund_id四个参数必填一个！")

        return self.post_model(url, input_obj, timeout)

    def download_bill(self, input_obj, timeout=6):
        """
        下载对账单，WxPayDownloadBill中bill_date为必填参数
        appid、mchid、spbill_create_ip、nonce_str不需要填入
        :param input_obj: WxPayDownloadBill
        :type input_obj: app.commons.wxpay.models.WxPayDownloadBill
        :param timeout:
        :type timeout:
        :return:
        :rtype:
        """
        url = "https://api.mch.weixin.qq.com/pay/downloadbill"
        if not input_obj.is_bill_date_set():
            raise WxPayError(u"对账单接口中，缺少必填参数bill_date！")

        input_obj.appid = self.__app_id
        input_obj.mch_id = self.__mch_id
        input_obj.nonce_str = self.gen_noce_str()
        input_obj.sign = self.make_sign(input_obj)
        xml = input_obj.to_xml()
        r = requests.request(
            method='post',
            url=url,
            timeout=timeout,
            **{"data": xml}
        )
        r.encoding = 'UTF-8'
        r.raise_for_status()
        response = r.text.encode('utf-8')

        if response.startswith("<xml>"):
            return ""
        return response

    def micropay(self, input_obj, timeout=10):
        """
        提交被扫支付API
        收银员使用扫码设备读取微信用户刷卡授权码以后，二维码或条码信息传送至商户收银台，
        由商户收银台或者商户后台调用该接口发起支付。
        :param input_obj: WxPayMicroPay
        :type input_obj: app.commons.wxpay.models.WxPayMicroPay
        :param timeout:
        :type timeout:
        :return:
        :rtype:
        """
        url = "https://api.mch.weixin.qq.com/pay/micropay"
        # 检测必填参数
        if not input_obj.is_body_set():
            raise WxPayError(u"提交被扫支付API接口中，缺少必填参数body！")
        elif not input_obj.is_out_trade_no_set():
            raise WxPayError(u"提交被扫支付API接口中，缺少必填参数out_trade_no！")
        elif not input_obj.is_total_fee_set():
            raise WxPayError(u"提交被扫支付API接口中，缺少必填参数total_fee！")
        elif not input_obj.is_auth_code_set():
            raise WxPayError(u"提交被扫支付API接口中，缺少必填参数auth_code！")

        input_obj.spbill_create_ip = self.__remote_address
        return self.post_model(url, input_obj, timeout)

    def reverse(self, input_obj, timeout=6):
        """
        撤销订单API接口，WxPayReverse中参数out_trade_no和transaction_id必须填写一个
        appid、mchid、spbill_create_ip、nonce_str不需要填入
        :param input_obj: WxPayReverse
        :type input_obj: app.commons.wxpay.models.WxPayReverse
        :param timeout:
        :type timeout:
        :return:
        :rtype:
        """
        url = "https://api.mch.weixin.qq.com/secapi/pay/reverse"
        # 检测必填参数
        if (not input_obj.is_out_trade_no_set()) and \
                (not input_obj.is_transaction_id_set()):
            raise WxPayError(u"撤销订单API接口中，参数out_trade_no和transaction_id必须填写一个！")

        return self.post_model(url, input_obj, timeout)

    def report(self, input_obj, timeout=1):
        """
        测速上报，该方法内部封装在report中，使用时请注意异常流程
        WxPayReport中interface_url、return_code、result_code、user_ip、execute_time_必填
        appid、mchid、spbill_create_ip、nonce_str不需要填入

        :param input_obj:
        :type input_obj: app.commons.wxpay.models.WxPayReport
        :param time_out:
        :type time_out:
        :return:
        :rtype: dict
        """

        url = "https://api.mch.weixin.qq.com/payitil/report"
        if not input_obj.is_interface_url_set():
            raise WxPayError(u"接口URL，缺少必填参数interface_url！")
        if not input_obj.is_return_code_set():
            raise WxPayError(u"返回状态码，缺少必填参数return_code！")
        if not input_obj.is_result_code_set():
            raise WxPayError(u"业务结果，缺少必填参数result_code！")
        if not input_obj.is_user_ip_set():
            raise WxPayError(u"返回状态码，缺少必填参数user_ip！")
        if not input_obj.is_execute_time__set():
            raise WxPayError(u"返回状态码，缺少必填参数execute_time_！")

        input_obj.user_ip = self.__remote_address
        input_obj.time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        input_obj.appid = self.__app_id
        input_obj.mch_id = self.__mch_id
        input_obj.nonce_str = self.gen_noce_str()

        input_obj.sign = self.make_sign(input_obj)
        xml = input_obj.to_xml()

        r = requests.request(
            method='post',
            url=url,
            timeout=timeout,
            **{"data": xml}
        )
        r.encoding = 'UTF-8'
        r.raise_for_status()
        xml_response = XMLStore(r.text.encode('utf-8'))
        return xml_response.xml2dict

    def bizpayurl(self, input_obj):
        """
        生成二维码规则,模式一生成支付二维码
        appid、mchid、spbill_create_ip、nonce_str不需要填入
        :param input_obj: WxPayBizPayUrl
        :type input_obj: app.commons.wxpay.models.WxPayBizPayUrl
        :param timeout:
        :type timeout:
        :return:
        :rtype: dict
        """
        if not input_obj.is_product_id_set():
            raise WxPayError(u"生成二维码，缺少必填参数product_id！")

        input_obj.appid = self.__app_id
        input_obj.mch_id = self.__mch_id
        input_obj.nonce_str = self.gen_noce_str()
        input_obj.time_stamp = int(time.time())
        input_obj.sign = self.make_sign(input_obj)
        return input_obj.get_values()

    def shorturl(self, input_obj, timeout=6):
        """
        转换短链接
        该接口主要用于扫码原生支付模式一中的二维码链接转成短链接(weixin://wxpay/s/XXXXXX)，
        减小二维码数据量，提升扫描速度和精确度。
        appid、mchid、spbill_create_ip、nonce_str不需要填入
        :param input_obj: WxPayShortUrl
        :type input_obj: app.commons.wxpay.models.WxPayShortUrl
        :param timeout:
        :type timeout:
        :return:
        :rtype:
        """
        url = "https://api.mch.weixin.qq.com/tools/shorturl"
        if not input_obj.is_long_url_set():
            raise WxPayError(u"需要转换的URL，签名用原串，传输需URL encode！")

        return self.post_model(url, input_obj, timeout)

    def xml_to_results(self, xml, check_sign=True):
        """
        将xml字符串转换成WxPayResults对象
        支付结果通用通知可用
        :param xml:
        :type xml:
        :param check_sign:
        :type check_sign:
        :return: WxPayResults
        :rtype: app.commons.wxpay.models.WxPayResults
        """
        wx_pay_results = WxPayResults.init_form_xml(xml)

        if check_sign and 'SUCCESS' == wx_pay_results.get_values().get('return_code', None):
            self.check_sign(wx_pay_results)

        return wx_pay_results

    def make_sign(self, input_obj):
        """
        生成签名

        :param input_obj:
        :type input_obj: app.commons.wxpay.models.WxPayModel
        :return:
        :rtype:
        """
        # 签名步骤一：按字典序排序参数
        data = input_obj.get_values()
        keys = data.keys()
        keys.sort()
        url_str = '&'.join(['%s=%s' % (key, data[key]) for key in keys
                            if key != 'sign' and key != '' and (not isinstance(key, dict))])
        # 签名步骤二：在string后加入KEY
        url_str += '&key=' + self.__key
        return hashlib.md5(url_str.encode('utf-8')).hexdigest().upper()

    def check_sign(self, input_obj):
        """
        签名检查

        :param input_obj:
        :type input_obj: app.commons.wxpay.models.WxPayModel
        :return:
        :rtype:
        """
        if not input_obj.is_sign_set():
            raise WxPayError("签名错误！")

        sign = self.make_sign(input_obj)
        if input_obj.sign == sign:
            return True
        raise WxPayError("签名错误！")

    def post_model(self, url, model, timeout, cert=False):
        """
        基础的model post方法，包含sign转xml逻辑
        :param url:
        :type url:
        :param model:
        :type model: app.commons.wxpay.models.WxPayModel
        :param timeout:
        :type timeout:
        :return:
        :rtype:
        """
        model.appid = self.__app_id
        model.mch_id = self.__mch_id
        model.nonce_str = self.gen_noce_str()
        model.sign = self.make_sign(model)
        xml = model.to_xml()
        return self.post_xml(url, xml, timeout, cert=cert)

    def post_xml(self, url, xml, timeout, check_sign=True, cert=False):

        start_time_stamp = self.timestamp()
        if cert:
            data = {
                "data": xml,
                "cert": cert
            }
        else:
            data = {
                "data": xml,
            }
        r = requests.request(
            method='post',
            url=url,
            timeout=timeout,
            **data
        )
        r.encoding = 'UTF-8'
        r.raise_for_status()

        wx_pay_results = self.xml_to_results(r.text.encode('utf-8'), check_sign)
        self.report_cost_time(url, start_time_stamp, wx_pay_results.get_values())
        return wx_pay_results

    def report_cost_time(self, url, start_time_stamp, data):
        """
        上报数据， 上报的时候将屏蔽所有异常流程

        :param url:
        :type url:
        :param start_time_stamp:
        :type start_time_stamp:
        :param data:
        :type data:
        :return:
        :rtype:
        """

        if self.__report_levenl == 0:
            return
        if self.__report_levenl == 1 \
                and 'SUCCESS' == data.get('return_code', None) \
                and 'SUCCESS' == data.get('result_code', None):
            return

        # 上报逻辑
        end_time_stamp = self.timestamp()
        obj_input = WxPayReport()
        obj_input.interface_url = url
        obj_input.execute_time_ = end_time_stamp - start_time_stamp

        if 'return_code' in data:
            obj_input.return_code = data.get('return_code', None)

        if 'return_msg' in data:
            obj_input.return_msg = data.get('return_msg', None)

        if 'result_code' in data:
            obj_input.result_code = data.get('result_code', None)

        if 'err_code' in data:
            obj_input.err_code = data.get('err_code', None)

        if 'err_code_des' in data:
            obj_input.err_code_des = data.get('err_code_des', None)

        if 'out_trade_no' in data:
            obj_input.out_trade_no = data.get('out_trade_no', None)

        if 'device_info' in data:
            obj_input.device_info = data.get('device_info', None)

        try:
            self.report(obj_input)
        except WxPayError:
            pass
