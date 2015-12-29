#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib
from wechat_sdk.lib import XMLStore
from wechat.wxpay.exceptions import WxPayError

__author__ = 'freeway'


class WxPayModel(object):
    """
    数据对象基础类，该类中定义数据类最基本的行为，包括：
    计算/设置/获取签名、输出xml格式的参数、从xml读取数据对象等
    """

    def __init__(self):
        self._values = dict()

    @property
    def sign(self):
        """
        获取签名
        :return:
        :rtype: str
        """
        return self._values['sign']

    @sign.setter
    def sign(self, sign):
        """
        生成并设置签名，详见签名生成算法
        :return:
        :rtype: str
        """
        self._values['sign'] = sign

    def is_sign_set(self):
        """
        判断签名，详见签名生成算法是否存在
        :return:
        :rtype: bool
        """
        return 'sign' in self._values

    def to_xml(self):
        """
        输出xml字符
        :return:
        :rtype:
        """
        xml = ["<xml>"]
        for k, v in self._values.iteritems():
            if isinstance(v, basestring):
                if v.isdigit():
                    xml.append("<{0}>{1}</{0}>".format(k, v))
                else:
                    xml.append("<{0}><![CDATA[{1}]]></{0}>".format(k, v))
            else:
                xml.append("<{0}>{1}</{0}>".format(k, str(v)))
        xml.append("</xml>")
        return "".join(xml)

    def from_xml(self, xml):
        """
        将xml转为dict
        :return:
        :rtype:
        """
        if not xml:
            raise WxPayError("xml数据异常！")
        s = XMLStore(xml)
        self._values = s.xml2dict
        return self._values

    def get_values(self):
        """
        获取设置的值
        :return:
        :rtype:
        """
        return self._values


class WxPayResults(WxPayModel):
    """
    接口调用结果类
    """

    @classmethod
    def init_form_dict(cls, data_dict):
        obj = cls()
        obj.form_dict(data_dict)
        return obj

    @classmethod
    def init_form_xml(cls, xml):
        obj = cls()
        obj.from_xml(xml)
        return obj

    def form_dict(self, dict_data):
        """
        使用字典初始化
        :param dict_data:
        :type dict_data: dict
        :return:
        :rtype: None
        """
        self._values = dict_data


class WxPayNotifyReply(WxPayModel):
    """
    回调基础类
    """

    @property
    def return_code(self):
        """
        获取错误码 FAIL 或者 SUCCESS
        """
        return self._values['return_code']

    @return_code.setter
    def return_code(self, return_code):
        """
        设置错误码 FAIL 或者 SUCCESS
        :param return_code: 错误码
        :type return_code:
        :return:
        :rtype: str
        """
        self._values['return_code'] = return_code

    @property
    def return_msg(self):
        """
        获取错误信息
        :return:
        :rtype:
        """
        return self._values['return_msg']

    @return_msg.setter
    def return_msg(self, return_msg):
        """
        设置错误信息
        :param return_msg:
        :type return_msg:
        """
        self._values['return_msg'] = return_msg

    def set_data(self, key, value):
        """
        设置返回参数
        :param key:
        :type key:
        :param value:
        :type value:
        :return:
        :rtype:
        """
        self._values[key] = value


class WxPayUnifiedOrder(WxPayModel):
    """
    统一下单输入对象
    """

    def __init__(self, openid, out_trade_no, trade_type, body, total_fee):
        super(WxPayUnifiedOrder, self).__init__()
        self.out_trade_no = out_trade_no
        self.body = body
        self.total_fee = total_fee
        self.trade_type = trade_type
        self.openid = openid

    @property
    def appid(self):
        """
        名称：公众账号ID
        必填：是
        类型：String(32)
        实例值：wx8888888888888888
        描述：微信分配的公众账号ID（企业号corpid即为此appId）
        """
        return self._values.get('appid', None)

    @appid.setter
    def appid(self, appid):
        self._values['appid'] = appid

    def is_appid_set(self):
        return 'appid' in self._values

    @property
    def mch_id(self):
        """
        名称：商户号
        必填：是
        类型：String(32)
        实例值：1900000109
        描述：微信支付分配的商户号
        """
        return self._values.get('mch_id', None)

    @mch_id.setter
    def mch_id(self, mch_id):
        self._values['mch_id'] = mch_id

    def is_mch_id_set(self):
        return 'mch_id' in self._values

    @property
    def device_info(self):
        """
        名称：设备号
        必填：否
        类型：String(32)
        实例值：013467007045764
        描述：终端设备号(门店号或收银设备ID)，注意：PC网页或公众号内支付请传"WEB"
        """
        return self._values.get('device_info', None)

    @device_info.setter
    def device_info(self, device_info):
        self._values['device_info'] = device_info

    def is_device_info_set(self):
        return 'device_info' in self._values

    @property
    def nonce_str(self):
        """
        名称：随机字符串
        必填：是
        类型：String(32)
        实例值：5K8264ILTKCH16CQ2502SI8ZNMTM67VS
        描述：随机字符串，不长于32位。推荐随机数生成算法
        """
        return self._values.get('nonce_str', None)

    @nonce_str.setter
    def nonce_str(self, nonce_str):
        self._values['nonce_str'] = nonce_str

    def is_nonce_str_set(self):
        return 'nonce_str' in self._values

    @property
    def body(self):
        """
        名称：商品描述
        必填：是
        类型：String(32)
        实例值：Ipad mini  16G  白色
        描述：商品或支付单简要描述
        """
        return self._values.get('body', None)

    @body.setter
    def body(self, body):
        self._values['body'] = body

    def is_body_set(self):
        return 'body' in self._values

    @property
    def detail(self):
        """
        名称：商品详情
        必填：否
        类型：String(8192)
        实例值：Ipad mini  16G  白色
        描述：商品名称明细列表
        """
        return self._values.get('detail', None)

    @detail.setter
    def detail(self, detail):
        self._values['detail'] = detail

    def is_detail_set(self):
        return 'detail' in self._values

    @property
    def attach(self):
        """
        名称：附加数据
        必填：否
        类型：String(127)
        实例值：说明
        描述：附加数据，在查询API和支付通知中原样返回，该字段主要用于商户携带订单的自定义数据
        """
        return self._values.get('attach', None)

    @attach.setter
    def attach(self, attach):
        self._values['attach'] = attach

    def is_attach_set(self):
        return 'attach' in self._values

    @property
    def out_trade_no(self):
        """
        名称：商户订单号
        必填：是
        类型：String(32)
        实例值：1217752501201407033233368018
        描述：商户系统内部的订单号,32个字符内、可包含字母, 其他说明见商户订单号
        """
        return self._values.get('out_trade_no', None)

    @out_trade_no.setter
    def out_trade_no(self, out_trade_no):
        self._values['out_trade_no'] = out_trade_no

    def is_out_trade_no_set(self):
        return 'out_trade_no' in self._values

    @property
    def fee_type(self):
        """
        名称：货币类型
        必填：否
        类型：String(16)
        实例值：CNY
        描述：符合ISO 4217标准的三位字母代码，默认人民币：CNY，其他值列表详见货币类型
        """
        return self._values.get('fee_type', None)

    @fee_type.setter
    def fee_type(self, fee_type):
        self._values['fee_type'] = fee_type

    def is_fee_type_set(self):
        return 'fee_type' in self._values

    @property
    def total_fee(self):
        """
        名称：总金额
        必填：是
        类型：Int
        实例值：888
        描述：订单总金额，只能为整数，详见支付金额
        """
        return self._values.get('total_fee', None)

    @total_fee.setter
    def total_fee(self, total_fee):
        self._values['total_fee'] = total_fee

    def is_total_fee_set(self):
        return 'total_fee' in self._values

    @property
    def spbill_create_ip(self):
        """
        名称：终端IP
        必填：是
        类型：String(16)
        实例值：8.8.8.8
        描述：APP和网页支付提交用户端ip，Native支付填调用微信支付API的机器IP。
        """
        return self._values.get('spbill_create_ip', None)

    @spbill_create_ip.setter
    def spbill_create_ip(self, spbill_create_ip):
        self._values['spbill_create_ip'] = spbill_create_ip

    def is_spbill_create_ip_set(self):
        return 'spbill_create_ip' in self._values

    @property
    def time_start(self):
        """
        名称：交易起始时间
        必填：否
        类型：String(14)
        实例值：20091225091010
        描述：订单生成时间，格式为yyyyMMddHHmmss，如2009年12月25日9点10分10秒表示为20091225091010。其他详见时间规则
        """
        return self._values.get('time_start', None)

    @time_start.setter
    def time_start(self, time_start):
        self._values['time_start'] = time_start

    def is_time_start_set(self):
        return 'time_start' in self._values

    @property
    def time_expire(self):
        """
        名称：交易结束时间
        必填：否
        类型：String(14)
        实例值：20091227091010
        描述：
                        订单失效时间，格式为yyyyMMddHHmmss，如2009年12月27日9点10分10秒表示为20091227091010。其他详见时间规则注意：最短失效时间间隔必须大于5分钟
        """
        return self._values.get('time_expire', None)

    @time_expire.setter
    def time_expire(self, time_expire):
        self._values['time_expire'] = time_expire

    def is_time_expire_set(self):
        return 'time_expire' in self._values

    @property
    def goods_tag(self):
        """
        名称：商品标记
        必填：否
        类型：String(32)
        实例值：WXG
        描述：商品标记，代金券或立减优惠功能的参数，说明详见代金券或立减优惠
        """
        return self._values.get('goods_tag', None)

    @goods_tag.setter
    def goods_tag(self, goods_tag):
        self._values['goods_tag'] = goods_tag

    def is_goods_tag_set(self):
        return 'goods_tag' in self._values

    @property
    def notify_url(self):
        """
        名称：通知地址
        必填：是
        类型：String(256)
        实例值：http://www.baidu.com
        描述：接收微信支付异步通知回调地址
        """
        return self._values.get('notify_url', None)

    @notify_url.setter
    def notify_url(self, notify_url):
        self._values['notify_url'] = notify_url

    def is_notify_url_set(self):
        return 'notify_url' in self._values

    @property
    def trade_type(self):
        """
        名称：交易类型
        必填：是
        类型：String(16)
        实例值：JSAPI
        描述：取值如下：JSAPI，NATIVE，APP，WAP,详细说明见参数规定
        """
        return self._values.get('trade_type', None)

    @trade_type.setter
    def trade_type(self, trade_type):
        self._values['trade_type'] = trade_type

    def is_trade_type_set(self):
        return 'trade_type' in self._values

    @property
    def product_id(self):
        """
        名称：商品ID
        必填：否
        类型：String(32)
        实例值：12235413214070356458058
        描述：trade_type=NATIVE，此参数必传。此id为二维码中包含的商品ID，商户自行定义。
        """
        return self._values.get('product_id', None)

    @product_id.setter
    def product_id(self, product_id):
        self._values['product_id'] = product_id

    def is_product_id_set(self):
        return 'product_id' in self._values

    @property
    def limit_pay(self):
        """
        名称：指定支付方式
        必填：否
        类型：String(32)
        实例值：no_credit
        描述：no_credit--指定不能使用信用卡支付
        """
        return self._values.get('limit_pay', None)

    @limit_pay.setter
    def limit_pay(self, limit_pay):
        self._values['limit_pay'] = limit_pay

    def is_limit_pay_set(self):
        return 'limit_pay' in self._values

    @property
    def openid(self):
        """
        名称：用户标识
        必填：否
        类型：String(128)
        实例值：oUpF8uMuAJO_M2pxb1Q9zNjWeS6o
        描述：trade_type=JSAPI，此参数必传，用户在商户appid下的唯一标识。openid如何获取，可参考【获取openid】。企业号请使用【企业号OAuth2.0接口】获取企业号内成员userid，再调用【企业号userid转openid接口】进行转换
        """
        return self._values.get('openid', None)

    @openid.setter
    def openid(self, openid):
        self._values['openid'] = openid

    def is_openid_set(self):
        return 'openid' in self._values


class WxPayOrderQuery(WxPayModel):
    """
    订单查询输入对象
    """

    @property
    def appid(self):
        """
        名称：公众账号ID
        必填：是
        类型：String(32)
        实例值：wxd678efh567hg6787
        描述：微信分配的公众账号ID（企业号corpid即为此appId）
        """
        return self._values.get('appid', None)

    @appid.setter
    def appid(self, appid):
        self._values['appid'] = appid

    def is_appid_set(self):
        return 'appid' in self._values

    @property
    def mch_id(self):
        """
        名称：商户号
        必填：是
        类型：String(32)
        实例值：1230000109
        描述：微信支付分配的商户号
        """
        return self._values.get('mch_id', None)

    @mch_id.setter
    def mch_id(self, mch_id):
        self._values['mch_id'] = mch_id

    def is_mch_id_set(self):
        return 'mch_id' in self._values

    @property
    def transaction_id(self):
        """
        名称：微信订单号
        必填：transaction_id out_trade_no二选一
        类型：String(32)
        实例值：1009660380201506130728806387
        描述：微信的订单号，优先使用
        """
        return self._values.get('transaction_id', None)

    @transaction_id.setter
    def transaction_id(self, transaction_id):
        self._values['transaction_id'] = transaction_id

    def is_transaction_id_set(self):
        return 'transaction_id' in self._values

    @property
    def out_trade_no(self):
        """
        名称：商户订单号
        必填：transaction_id out_trade_no二选一
        类型：String(32)
        实例值：20150806125346
        描述：商户系统内部的订单号，当没提供transaction_id时需要传这个。
        """
        return self._values.get('out_trade_no', None)

    @out_trade_no.setter
    def out_trade_no(self, out_trade_no):
        self._values['out_trade_no'] = out_trade_no

    def is_out_trade_no_set(self):
        return 'out_trade_no' in self._values

    @property
    def nonce_str(self):
        """
        名称：随机字符串
        必填：是
        类型：String(32)
        实例值：C380BEC2BFD727A4B6845133519F3AD6
        描述：随机字符串，不长于32位。推荐随机数生成算法
        """
        return self._values.get('nonce_str', None)

    @nonce_str.setter
    def nonce_str(self, nonce_str):
        self._values['nonce_str'] = nonce_str

    def is_nonce_str_set(self):
        return 'nonce_str' in self._values

    @property
    def sign(self):
        """
        名称：签名
        必填：是
        类型：String(32)
        实例值：5K8264ILTKCH16CQ2502SI8ZNMTM67VS
        描述：签名，详见签名生成算法
        """
        return self._values.get('sign', None)

    @sign.setter
    def sign(self, sign):
        self._values['sign'] = sign

    def is_sign_set(self):
        return 'sign' in self._values


class WxPayCloseOrder(WxPayModel):
    """
    关闭订单输入对象
    """

    @property
    def appid(self):
        """
        名称：公众账号ID
        必填：是
        类型：String(32)
        实例值：wx8888888888888888
        描述：微信分配的公众账号ID（企业号corpid即为此appId）
        """
        return self._values.get('appid', None)

    @appid.setter
    def appid(self, appid):
        self._values['appid'] = appid

    def is_appid_set(self):
        return 'appid' in self._values

    @property
    def mch_id(self):
        """
        名称：商户号
        必填：是
        类型：String(32)
        实例值：1900000109
        描述：微信支付分配的商户号
        """
        return self._values.get('mch_id', None)

    @mch_id.setter
    def mch_id(self, mch_id):
        self._values['mch_id'] = mch_id

    def is_mch_id_set(self):
        return 'mch_id' in self._values

    @property
    def out_trade_no(self):
        """
        名称：商户订单号
        必填：是
        类型：String(32)
        实例值：1217752501201407033233368018
        描述：商户系统内部的订单号
        """
        return self._values.get('out_trade_no', None)

    @out_trade_no.setter
    def out_trade_no(self, out_trade_no):
        self._values['out_trade_no'] = out_trade_no

    def is_out_trade_no_set(self):
        return 'out_trade_no' in self._values

    @property
    def nonce_str(self):
        """
        名称：随机字符串
        必填：是
        类型：String(32)
        实例值：5K8264ILTKCH16CQ2502SI8ZNMTM67VS
        描述：商户系统内部的订单号,32个字符内、可包含字母, 其他说明见商户订单号
        """
        return self._values.get('nonce_str', None)

    @nonce_str.setter
    def nonce_str(self, nonce_str):
        self._values['nonce_str'] = nonce_str

    def is_nonce_str_set(self):
        return 'nonce_str' in self._values


class WxPayRefund(WxPayModel):
    """
    提交退款输入对象
    """

    def __init__(self, out_trade_no, out_refund_no, total_fee, refund_fee):
        super(WxPayRefund, self).__init__()
        self.out_trade_no = out_trade_no
        self.out_refund_no = out_refund_no
        self.total_fee = total_fee
        self.refund_fee = refund_fee

    @property
    def appid(self):
        """
        名称：公众账号ID
        必填：是
        类型：String(32)
        实例值：wx8888888888888888
        描述：微信分配的公众账号ID（企业号corpid即为此appId）
        """
        return self._values.get('appid', None)

    @appid.setter
    def appid(self, appid):
        self._values['appid'] = appid

    def is_appid_set(self):
        return 'appid' in self._values

    @property
    def mch_id(self):
        """
        名称：商户号
        必填：是
        类型：String(32)
        实例值：1900000109
        描述：微信支付分配的商户号
        """
        return self._values.get('mch_id', None)

    @mch_id.setter
    def mch_id(self, mch_id):
        self._values['mch_id'] = mch_id

    def is_mch_id_set(self):
        return 'mch_id' in self._values

    @property
    def device_info(self):
        """
        名称：设备号
        必填：否
        类型：String(32)
        实例值：013467007045764
        描述：终端设备号
        """
        return self._values.get('device_info', None)

    @device_info.setter
    def device_info(self, device_info):
        self._values['device_info'] = device_info

    def is_device_info_set(self):
        return 'device_info' in self._values

    @property
    def nonce_str(self):
        """
        名称：随机字符串
        必填：是
        类型：String(32)
        实例值：5K8264ILTKCH16CQ2502SI8ZNMTM67VS
        描述：随机字符串，不长于32位。推荐随机数生成算法
        """
        return self._values.get('nonce_str', None)

    @nonce_str.setter
    def nonce_str(self, nonce_str):
        self._values['nonce_str'] = nonce_str

    def is_nonce_str_set(self):
        return 'nonce_str' in self._values

    @property
    def transaction_id(self):
        """
        名称：微信订单号
        必填：transaction_id out_trade_no二选一
        类型：String(28)
        实例值：1217752501201407033233368018
        描述：微信生成的订单号，在支付通知中有返回
        """
        return self._values.get('transaction_id', None)

    @transaction_id.setter
    def transaction_id(self, transaction_id):
        self._values['transaction_id'] = transaction_id

    def is_transaction_id_set(self):
        return 'transaction_id' in self._values

    @property
    def out_trade_no(self):
        """
        名称：商户订单号
        必填：transaction_id out_trade_no二选一
        类型：String(32)
        实例值：1217752501201407033233368018
        描述：商户侧传给微信的订单号
        """
        return self._values.get('out_trade_no', None)

    @out_trade_no.setter
    def out_trade_no(self, out_trade_no):
        self._values['out_trade_no'] = out_trade_no

    def is_out_trade_no_set(self):
        return 'out_trade_no' in self._values

    @property
    def out_refund_no(self):
        """
        名称：商户退款单号
        必填：是
        类型：String(32)
        实例值：1217752501201407033233368018
        描述：商户系统内部的退款单号，商户系统内部唯一，同一退款单号多次请求只退一笔
        """
        return self._values.get('out_refund_no', None)

    @out_refund_no.setter
    def out_refund_no(self, out_refund_no):
        self._values['out_refund_no'] = out_refund_no

    def is_out_refund_no_set(self):
        return 'out_refund_no' in self._values

    @property
    def total_fee(self):
        """
        名称：总金额
        必填：是
        类型：Int
        实例值：100
        描述：订单总金额，单位为分，只能为整数，详见支付金额
        """
        return self._values.get('total_fee', None)

    @total_fee.setter
    def total_fee(self, total_fee):
        self._values['total_fee'] = total_fee

    def is_total_fee_set(self):
        return 'total_fee' in self._values

    @property
    def refund_fee(self):
        """
        名称：退款金额
        必填：是
        类型：Int
        实例值：100
        描述：退款总金额，订单总金额，单位为分，只能为整数，详见支付金额
        """
        return self._values.get('refund_fee', None)

    @refund_fee.setter
    def refund_fee(self, refund_fee):
        self._values['refund_fee'] = refund_fee

    def is_refund_fee_set(self):
        return 'refund_fee' in self._values

    @property
    def refund_fee_type(self):
        """
        名称：货币种类
        必填：否
        类型：String(8)
        实例值：CNY
        描述：货币类型，符合ISO 4217标准的三位字母代码，默认人民币：CNY，其他值列表详见货币类型
        """
        return self._values.get('refund_fee_type', None)

    @refund_fee_type.setter
    def refund_fee_type(self, refund_fee_type):
        self._values['refund_fee_type'] = refund_fee_type

    def is_refund_fee_type_set(self):
        return 'refund_fee_type' in self._values

    @property
    def op_user_id(self):
        """
        名称：操作员
        必填：是
        类型：String(32)
        实例值：1900000109
        描述：操作员帐号, 默认为商户号
        """
        return self._values.get('op_user_id', None)

    @op_user_id.setter
    def op_user_id(self, op_user_id):
        self._values['op_user_id'] = op_user_id

    def is_op_user_id_set(self):
        return 'op_user_id' in self._values


class WxPayRefundQuery(WxPayModel):
    """
    退款查询输入对象
    """

    @property
    def appid(self):
        """
        名称：公众账号ID
        必填：是
        类型：String(32)
        实例值：wx8888888888888888
        描述：微信分配的公众账号ID（企业号corpid即为此appId）
        """
        return self._values.get('appid', None)

    @appid.setter
    def appid(self, appid):
        self._values['appid'] = appid

    def is_appid_set(self):
        return 'appid' in self._values

    @property
    def mch_id(self):
        """
        名称：商户号
        必填：是
        类型：String(32)
        实例值：1900000109
        描述：微信支付分配的商户号
        """
        return self._values.get('mch_id', None)

    @mch_id.setter
    def mch_id(self, mch_id):
        self._values['mch_id'] = mch_id

    def is_mch_id_set(self):
        return 'mch_id' in self._values

    @property
    def device_info(self):
        """
        名称：设备号
        必填：否
        类型：String(32)
        实例值：013467007045764
        描述：商户自定义的终端设备号，如门店编号、设备的ID等
        """
        return self._values.get('device_info', None)

    @device_info.setter
    def device_info(self, device_info):
        self._values['device_info'] = device_info

    def is_device_info_set(self):
        return 'device_info' in self._values

    @property
    def nonce_str(self):
        """
        名称：随机字符串
        必填：是
        类型：String(32)
        实例值：5K8264ILTKCH16CQ2502SI8ZNMTM67VS
        描述：随机字符串，不长于32位。推荐随机数生成算法
        """
        return self._values.get('nonce_str', None)

    @nonce_str.setter
    def nonce_str(self, nonce_str):
        self._values['nonce_str'] = nonce_str

    def is_nonce_str_set(self):
        return 'nonce_str' in self._values

    @property
    def transaction_id(self):
        """
        名称：微信订单号
        必填：transaction_id out_trade_no out_refund_no refund_id四选一
        类型：String(28)
        实例值：1217752501201407033233368018
        描述：微信订单号
        """
        return self._values.get('transaction_id', None)

    @transaction_id.setter
    def transaction_id(self, transaction_id):
        self._values['transaction_id'] = transaction_id

    def is_transaction_id_set(self):
        return 'transaction_id' in self._values

    @property
    def out_trade_no(self):
        """
        名称：商户订单号
        必填：transaction_id out_trade_no out_refund_no refund_id四选一
        类型：String(32)
        实例值：1217752501201407033233368018
        描述：商户系统内部的订单号
        """
        return self._values.get('out_trade_no', None)

    @out_trade_no.setter
    def out_trade_no(self, out_trade_no):
        self._values['out_trade_no'] = out_trade_no

    def is_out_trade_no_set(self):
        return 'out_trade_no' in self._values

    @property
    def out_refund_no(self):
        """
        名称：商户退款单号
        必填：transaction_id out_trade_no out_refund_no refund_id四选一
        类型：String(32)
        实例值：1217752501201407033233368018
        描述：商户侧传给微信的退款单号
        """
        return self._values.get('out_refund_no', None)

    @out_refund_no.setter
    def out_refund_no(self, out_refund_no):
        self._values['out_refund_no'] = out_refund_no

    def is_out_refund_no_set(self):
        return 'out_refund_no' in self._values

    @property
    def refund_id(self):
        """
        名称：微信退款单号
        必填：transaction_id out_trade_no out_refund_no refund_id四选一
        类型：String(28)
        实例值：1217752501201407033233368018
        描述：微信生成的退款单号，在申请退款接口有返回
        """
        return self._values.get('refund_id', None)

    @refund_id.setter
    def refund_id(self, refund_id):
        self._values['refund_id'] = refund_id

    def is_refund_id_set(self):
        return 'refund_id' in self._values


class WxPayDownloadBill(WxPayModel):
    """
    下载对账单输入对象
    """

    @property
    def appid(self):
        """
        名称：公众账号ID
        必填：是
        类型：String(32)
        实例值：wx8888888888888888
        描述：微信分配的公众账号ID（企业号corpid即为此appId）
        """
        return self._values.get('appid', None)

    @appid.setter
    def appid(self, appid):
        self._values['appid'] = appid

    def is_appid_set(self):
        return 'appid' in self._values

    @property
    def mch_id(self):
        """
        名称：商户号
        必填：是
        类型：String(32)
        实例值：1900000109
        描述：微信支付分配的商户号
        """
        return self._values.get('mch_id', None)

    @mch_id.setter
    def mch_id(self, mch_id):
        self._values['mch_id'] = mch_id

    def is_mch_id_set(self):
        return 'mch_id' in self._values

    @property
    def device_info(self):
        """
        名称：设备号
        必填：否
        类型：String(32)
        实例值：013467007045764
        描述：微信支付分配的终端设备号，填写此字段，只下载该设备号的对账单
        """
        return self._values.get('device_info', None)

    @device_info.setter
    def device_info(self, device_info):
        self._values['device_info'] = device_info

    def is_device_info_set(self):
        return 'device_info' in self._values

    @property
    def nonce_str(self):
        """
        名称：随机字符串
        必填：是
        类型：String(32)
        实例值：5K8264ILTKCH16CQ2502SI8ZNMTM67VS
        描述：随机字符串，不长于32位。推荐随机数生成算法
        """
        return self._values.get('nonce_str', None)

    @nonce_str.setter
    def nonce_str(self, nonce_str):
        self._values['nonce_str'] = nonce_str

    def is_nonce_str_set(self):
        return 'nonce_str' in self._values

    @property
    def bill_date(self):
        """
        名称：对账单日期
        必填：是
        类型：String(8)
        实例值：20140603
        描述：下载对账单的日期，格式：20140603
        """
        return self._values.get('bill_date', None)

    @bill_date.setter
    def bill_date(self, bill_date):
        self._values['bill_date'] = bill_date

    def is_bill_date_set(self):
        return 'bill_date' in self._values

    @property
    def bill_type(self):
        """
        名称：账单类型
        必填：否
        类型：String(8)
        实例值：ALL
        描述：
                        ALL，返回当日所有订单信息，默认值
                        SUCCESS，返回当日成功支付的订单
                        REFUND，返回当日退款订单
                        REVOKED，已撤销的订单

        """
        return self._values.get('bill_type', None)

    @bill_type.setter
    def bill_type(self, bill_type):
        self._values['bill_type'] = bill_type

    def is_bill_type_set(self):
        return 'bill_type' in self._values


class WxPayReport(WxPayModel):
    """
    测速上报输入对象
    """

    @property
    def appid(self):
        """
        名称：公众账号ID
        必填：否
        类型：String(32)
        实例值：wx8888888888888888
        描述：微信分配的公众账号ID（企业号corpid即为此appId）
        """
        return self._values.get('appid', None)

    @appid.setter
    def appid(self, appid):
        self._values['appid'] = appid

    def is_appid_set(self):
        return 'appid' in self._values

    @property
    def mch_id(self):
        """
        名称：商户号
        必填：是
        类型：String(32)
        实例值：1900000109
        描述：微信支付分配的商户号
        """
        return self._values.get('mch_id', None)

    @mch_id.setter
    def mch_id(self, mch_id):
        self._values['mch_id'] = mch_id

    def is_mch_id_set(self):
        return 'mch_id' in self._values

    @property
    def device_info(self):
        """
        名称：设备号
        必填：否
        类型：String(32)
        实例值：013467007045764
        描述：微信支付分配的终端设备号，商户自定义
        """
        return self._values.get('device_info', None)

    @device_info.setter
    def device_info(self, device_info):
        self._values['device_info'] = device_info

    def is_device_info_set(self):
        return 'device_info' in self._values

    @property
    def nonce_str(self):
        """
        名称：随机字符串
        必填：是
        类型：String(32)
        实例值：5K8264ILTKCH16CQ2502SI8ZNMTM67VS
        描述：随机字符串，不长于32位。推荐随机数生成算法
        """
        return self._values.get('nonce_str', None)

    @nonce_str.setter
    def nonce_str(self, nonce_str):
        self._values['nonce_str'] = nonce_str

    def is_nonce_str_set(self):
        return 'nonce_str' in self._values

    @property
    def interface_url(self):
        """
        名称：接口URL
        必填：是
        类型：String(127)
        实例值：https://api.mch.weixin.qq.com/pay/unifiedorder
        描述：
                        报对应的接口的完整URL，类似：
                        https://api.mch.weixin.qq.com/pay/unifiedorder
                        对于刷卡支付，为更好的和商户共同分析一次业务行为的整体耗时情况，对于两种接入模式，请都在门店侧对一次刷卡支付进行一次单独的整体上报，上报URL指定为：
                        https://api.mch.weixin.qq.com/pay/micropay/total
                        关于两种接入模式具体可参考本文档章节：刷卡支付商户接入模式
                        其它接口调用仍然按照调用一次，上报一次来进行。

        """
        return self._values.get('interface_url', None)

    @interface_url.setter
    def interface_url(self, interface_url):
        self._values['interface_url'] = interface_url

    def is_interface_url_set(self):
        return 'interface_url' in self._values

    @property
    def execute_time_(self):
        """
        名称：接口耗时
        必填：是
        类型：Int
        实例值：1000
        描述：接口耗时情况，单位为毫秒
        """
        return self._values.get('execute_time_', None)

    @execute_time_.setter
    def execute_time_(self, execute_time_):
        self._values['execute_time_'] = execute_time_

    def is_execute_time__set(self):
        return 'execute_time_' in self._values

    @property
    def return_code(self):
        """
        名称：返回状态码
        必填：是
        类型：String(16)
        实例值：SUCCESS
        描述：
                        SUCCESS/FAIL
                        此字段是通信标识，非交易标识，交易是否成功需要查看trade_state来判断

        """
        return self._values.get('return_code', None)

    @return_code.setter
    def return_code(self, return_code):
        self._values['return_code'] = return_code

    def is_return_code_set(self):
        return 'return_code' in self._values

    @property
    def return_msg(self):
        """
        名称：返回信息
        必填：否
        类型：String(128)
        实例值：签名失败
        描述：
                        返回信息，如非空，为错误原因
                        签名失败
                        参数格式校验错误

        """
        return self._values.get('return_msg', None)

    @return_msg.setter
    def return_msg(self, return_msg):
        self._values['return_msg'] = return_msg

    def is_return_msg_set(self):
        return 'return_msg' in self._values

    @property
    def result_code(self):
        """
        名称：业务结果
        必填：是
        类型：String(16)
        实例值：SUCCESS
        描述：SUCCESS/FAIL
        """
        return self._values.get('result_code', None)

    @result_code.setter
    def result_code(self, result_code):
        self._values['result_code'] = result_code

    def is_result_code_set(self):
        return 'result_code' in self._values

    @property
    def err_code(self):
        """
        名称：错误代码
        必填：否
        类型：String(32)
        实例值：SYSTEMERROR
        描述：
                        ORDERNOTEXIST—订单不存在
                        SYSTEMERROR—系统错误

        """
        return self._values.get('err_code', None)

    @err_code.setter
    def err_code(self, err_code):
        self._values['err_code'] = err_code

    def is_err_code_set(self):
        return 'err_code' in self._values

    @property
    def err_code_des(self):
        """
        名称：错误代码描述
        必填：否
        类型：String(128)
        实例值：系统错误
        描述：结果信息描述
        """
        return self._values.get('err_code_des', None)

    @err_code_des.setter
    def err_code_des(self, err_code_des):
        self._values['err_code_des'] = err_code_des

    def is_err_code_des_set(self):
        return 'err_code_des' in self._values

    @property
    def out_trade_no(self):
        """
        名称：商户订单号
        必填：否
        类型：String(32)
        实例值：1217752501201407033233368018
        描述：商户系统内部的订单号,商户可以在上报时提供相关商户订单号方便微信支付更好的提高服务质量。 
        """
        return self._values.get('out_trade_no', None)

    @out_trade_no.setter
    def out_trade_no(self, out_trade_no):
        self._values['out_trade_no'] = out_trade_no

    def is_out_trade_no_set(self):
        return 'out_trade_no' in self._values

    @property
    def user_ip(self):
        """
        名称：访问接口IP
        必填：是
        类型：String(16)
        实例值：8.8.8.8
        描述：发起接口调用时的机器IP 
        """
        return self._values.get('user_ip', None)

    @user_ip.setter
    def user_ip(self, user_ip):
        self._values['user_ip'] = user_ip

    def is_user_ip_set(self):
        return 'user_ip' in self._values

    @property
    def time(self):
        """
        名称：商户上报时间
        必填：否
        类型：String(14)
        实例值：20091227091010
        描述：系统时间，格式为yyyyMMddHHmmss，如2009年12月27日9点10分10秒表示为20091227091010。其他详见时间规则
        """
        return self._values.get('time', None)

    @time.setter
    def time(self, time):
        self._values['time'] = time

    def is_time_set(self):
        return 'time' in self._values


class WxPayShortUrl(WxPayModel):
    """
    短链转换输入对象
    """

    @property
    def appid(self):
        """
        名称：公众账号ID
        必填：是
        类型：String(32)
        实例值：wx8888888888888888
        描述：微信分配的公众账号ID（企业号corpid即为此appId）
        """
        return self._values.get('appid', None)

    @appid.setter
    def appid(self, appid):
        self._values['appid'] = appid

    def is_appid_set(self):
        return 'appid' in self._values

    @property
    def mch_id(self):
        """
        名称：商户号
        必填：是
        类型：String(32)
        实例值：1900000109
        描述：微信支付分配的商户号
        """
        return self._values.get('mch_id', None)

    @mch_id.setter
    def mch_id(self, mch_id):
        self._values['mch_id'] = mch_id

    def is_mch_id_set(self):
        return 'mch_id' in self._values

    @property
    def long_url(self):
        """
        名称：URL链接
        必填：是
        类型：String(512、
        实例值：weixin：//wxpay/bizpayurl?sign=XXXXX&appid=XXXXX&mch_id=XXXXX&product_id=XXXXXX&time_stamp=XXXXXX&nonce_str=XXXXX
        描述：需要转换的URL，签名用原串，传输需URLencode
        """
        return self._values.get('long_url', None)

    @long_url.setter
    def long_url(self, long_url):
        self._values['long_url'] = long_url

    def is_long_url_set(self):
        return 'long_url' in self._values

    @property
    def nonce_str(self):
        """
        名称：随机字符串
        必填：是
        类型：String(32)
        实例值：5K8264ILTKCH16CQ2502SI8ZNMTM67VS
        描述：随机字符串，不长于32位。推荐随机数生成算法
        """
        return self._values.get('nonce_str', None)

    @nonce_str.setter
    def nonce_str(self, nonce_str):
        self._values['nonce_str'] = nonce_str

    def is_nonce_str_set(self):
        return 'nonce_str' in self._values


class WxPayMicroPay(WxPayModel):
    """
    提交被扫输入对象
    """

    @property
    def appid(self):
        """
        名称：公众账号ID
        必填：String(32)
        类型：是
        实例值：wx8888888888888888
        描述：微信分配的公众账号ID（企业号corpid即为此appId）
        """
        return self._values.get('appid', None)

    @appid.setter
    def appid(self, appid):
        self._values['appid'] = appid

    def is_appid_set(self):
        return 'appid' in self._values

    @property
    def mch_id(self):
        """
        名称：商户号
        必填：String(32)
        类型：是
        实例值：1900000109
        描述：微信支付分配的商户号
        """
        return self._values.get('mch_id', None)

    @mch_id.setter
    def mch_id(self, mch_id):
        self._values['mch_id'] = mch_id

    def is_mch_id_set(self):
        return 'mch_id' in self._values

    @property
    def device_info(self):
        """
        名称：设备号
        必填：String(32)
        类型：否
        实例值：013467007045764
        描述：终端设备号(商户自定义，如门店编号)
        """
        return self._values.get('device_info', None)

    @device_info.setter
    def device_info(self, device_info):
        self._values['device_info'] = device_info

    def is_device_info_set(self):
        return 'device_info' in self._values

    @property
    def nonce_str(self):
        """
        名称：随机字符串
        必填：String(32)
        类型：是
        实例值：5K8264ILTKCH16CQ2502SI8ZNMTM67VS
        描述：随机字符串，不长于32位。推荐随机数生成算法
        """
        return self._values.get('nonce_str', None)

    @nonce_str.setter
    def nonce_str(self, nonce_str):
        self._values['nonce_str'] = nonce_str

    def is_nonce_str_set(self):
        return 'nonce_str' in self._values

    @property
    def body(self):
        """
        名称：商品描述
        必填：String(32)
        类型：是
        实例值：Ipadmini16G白色
        描述：商品或支付单简要描述
        """
        return self._values.get('body', None)

    @body.setter
    def body(self, body):
        self._values['body'] = body

    def is_body_set(self):
        return 'body' in self._values

    @property
    def detail(self):
        """
        名称：商品详情
        必填：String(8192)
        类型：否
        实例值：Ipadmini16G白色
        描述：商品名称明细列表
        """
        return self._values.get('detail', None)

    @detail.setter
    def detail(self, detail):
        self._values['detail'] = detail

    def is_detail_set(self):
        return 'detail' in self._values

    @property
    def attach(self):
        """
        名称：附加数据
        必填：String(127)
        类型：否
        实例值：说明
        描述：附加数据，在查询API和支付通知中原样返回，该字段主要用于商户携带订单的自定义数据
        """
        return self._values.get('attach', None)

    @attach.setter
    def attach(self, attach):
        self._values['attach'] = attach

    def is_attach_set(self):
        return 'attach' in self._values

    @property
    def out_trade_no(self):
        """
        名称：商户订单号
        必填：String(32)
        类型：是
        实例值：1217752501201407033233368018
        描述：商户系统内部的订单号,32个字符内、可包含字母,其他说明见商户订单号
        """
        return self._values.get('out_trade_no', None)

    @out_trade_no.setter
    def out_trade_no(self, out_trade_no):
        self._values['out_trade_no'] = out_trade_no

    def is_out_trade_no_set(self):
        return 'out_trade_no' in self._values

    @property
    def total_fee(self):
        """
        名称：总金额
        必填：Int
        类型：是
        实例值：888
        描述：订单总金额，单位为分，只能为整数，详见支付金额
        """
        return self._values.get('total_fee', None)

    @total_fee.setter
    def total_fee(self, total_fee):
        self._values['total_fee'] = total_fee

    def is_total_fee_set(self):
        return 'total_fee' in self._values

    @property
    def fee_type(self):
        """
        名称：货币类型
        必填：String(16)
        类型：否
        实例值：CNY
        描述：符合ISO4217标准的三位字母代码，默认人民币：CNY，其他值列表详见货币类型
        """
        return self._values.get('fee_type', None)

    @fee_type.setter
    def fee_type(self, fee_type):
        self._values['fee_type'] = fee_type

    def is_fee_type_set(self):
        return 'fee_type' in self._values

    @property
    def spbill_create_ip(self):
        """
        名称：终端IP
        必填：String(16)
        类型：是
        实例值：8.8.8.8
        描述：调用微信支付API的机器IP
        """
        return self._values.get('spbill_create_ip', None)

    @spbill_create_ip.setter
    def spbill_create_ip(self, spbill_create_ip):
        self._values['spbill_create_ip'] = spbill_create_ip

    def is_spbill_create_ip_set(self):
        return 'spbill_create_ip' in self._values

    @property
    def goods_tag(self):
        """
        名称：商品标记
        必填：String(32)
        类型：否
        实例值：
        描述：商品标记，代金券或立减优惠功能的参数，说明详见代金券或立减优惠
        """
        return self._values.get('goods_tag', None)

    @goods_tag.setter
    def goods_tag(self, goods_tag):
        self._values['goods_tag'] = goods_tag

    def is_goods_tag_set(self):
        return 'goods_tag' in self._values

    @property
    def limit_pay(self):
        """
        名称：指定支付方式
        必填：String(32)
        类型：否
        实例值：no_credit
        描述：no_credit--指定不能使用信用卡支付
        """
        return self._values.get('limit_pay', None)

    @limit_pay.setter
    def limit_pay(self, limit_pay):
        self._values['limit_pay'] = limit_pay

    def is_limit_pay_set(self):
        return 'limit_pay' in self._values

    @property
    def auth_code(self):
        """
        名称：授权码
        必填：String(128)
        类型：是
        实例值：120061098828009406
        描述：扫码支付授权码，设备读取用户微信中的条码或者二维码信息
        """
        return self._values.get('auth_code', None)

    @auth_code.setter
    def auth_code(self, auth_code):
        self._values['auth_code'] = auth_code

    def is_auth_code_set(self):
        return 'auth_code' in self._values


class WxPayReverse(WxPayModel):
    """
    撤销输入对象
    """

    @property
    def appid(self):
        """
        名称：公众账号ID
        必填：String(32)
        类型：是
        实例值：wx8888888888888888
        描述：微信分配的公众账号ID（企业号corpid即为此appId）
        """
        return self._values.get('appid', None)

    @appid.setter
    def appid(self, appid):
        self._values['appid'] = appid

    def is_appid_set(self):
        return 'appid' in self._values

    @property
    def mch_id(self):
        """
        名称：商户号
        必填：String(32)
        类型：是
        实例值：1900000109
        描述：微信支付分配的商户号
        """
        return self._values.get('mch_id', None)

    @mch_id.setter
    def mch_id(self, mch_id):
        self._values['mch_id'] = mch_id

    def is_mch_id_set(self):
        return 'mch_id' in self._values

    @property
    def transaction_id(self):
        """
        名称：微信订单号
        必填：String(32)
        类型：否
        实例值：1217752501201407033233368018
        描述：微信的订单号，优先使用
        """
        return self._values.get('transaction_id', None)

    @transaction_id.setter
    def transaction_id(self, transaction_id):
        self._values['transaction_id'] = transaction_id

    def is_transaction_id_set(self):
        return 'transaction_id' in self._values

    @property
    def out_trade_no(self):
        """
        名称：商户订单号
        必填：String(32)
        类型：是
        实例值：1217752501201407033233368018
        描述：商户系统内部的订单号,transaction_id、out_trade_no二选一，如果同时存在优先级：transaction_id> out_trade_no
        """
        return self._values.get('out_trade_no', None)

    @out_trade_no.setter
    def out_trade_no(self, out_trade_no):
        self._values['out_trade_no'] = out_trade_no

    def is_out_trade_no_set(self):
        return 'out_trade_no' in self._values

    @property
    def nonce_str(self):
        """
        名称：随机字符串
        必填：String(32)
        类型：是
        实例值：5K8264ILTKCH16CQ2502SI8ZNMTM67VS
        描述：随机字符串，不长于32位。推荐随机数生成算法
        """
        return self._values.get('nonce_str', None)

    @nonce_str.setter
    def nonce_str(self, nonce_str):
        self._values['nonce_str'] = nonce_str

    def is_nonce_str_set(self):
        return 'nonce_str' in self._values


class WxPayJsApiPay(WxPayModel):
    """
    提交JSAPI输入对象
    """

    @property
    def appId(self):
        """
        名称：公众号id
        必填：是
        类型：String(16)
        实例值：wx8888888888888888
        描述：商户注册具有支付权限的公众号成功后即可获得
        """
        return self._values.get('appId', None)

    @appId.setter
    def appId(self, appId):
        self._values['appId'] = appId

    def is_appId_set(self):
        return 'appId' in self._values

    @property
    def timeStamp(self):
        """
        名称：时间戳
        必填：是
        类型：String(32)
        实例值：1414561699
        描述：当前的时间，其他详见时间戳规则
        """
        return self._values.get('timeStamp', None)

    @timeStamp.setter
    def timeStamp(self, timeStamp):
        self._values['timeStamp'] = timeStamp

    def is_timeStamp_set(self):
        return 'timeStamp' in self._values

    @property
    def nonceStr(self):
        """
        名称：随机字符串
        必填：是
        类型：String(32)
        实例值：5K8264ILTKCH16CQ2502SI8ZNMTM67VS
        描述：随机字符串，不长于32位。推荐随机数生成算法
        """
        return self._values.get('nonceStr', None)

    @nonceStr.setter
    def nonceStr(self, nonceStr):
        self._values['nonceStr'] = nonceStr

    def is_nonceStr_set(self):
        return 'nonceStr' in self._values

    @property
    def package(self):
        """
        名称：订单详情扩展字符串
        必填：是
        类型：String(128)
        实例值：prepay_id=123456789
        描述：统一下单接口返回的prepay_id参数值，提交格式如：prepay_id=***
        """
        return self._values.get('package', None)

    @package.setter
    def package(self, package):
        self._values['package'] = package

    def is_package_set(self):
        return 'package' in self._values

    @property
    def signType(self):
        """
        名称：签名方式
        必填：是
        类型：String(32)
        实例值：MD5
        描述：签名算法，暂支持MD5
        """
        return self._values.get('signType', None)

    @signType.setter
    def signType(self, signType):
        self._values['signType'] = signType

    def is_signType_set(self):
        return 'signType' in self._values

    @property
    def paySign(self):
        """
        名称：签名
        必填：是
        类型：String(64)
        实例值：C380BEC2BFD727A4B6845133519F3AD6
        描述：签名，详见签名生成算法
        """
        return self._values.get('paySign', None)

    @paySign.setter
    def paySign(self, paySign):
        self._values['paySign'] = paySign

    def is_paySign_set(self):
        return 'paySign' in self._values


class WxPayBizPayUrl(WxPayModel):
    """
    扫码支付模式一生成二维码参数
    """

    @property
    def appid(self):
        """
        名称：公众账号ID
        必填：String(32)
        类型：是
        实例值：wx8888888888888888
        描述：微信分配的公众账号ID
        """
        return self._values.get('appid', None)

    @appid.setter
    def appid(self, appid):
        self._values['appid'] = appid

    def is_appid_set(self):
        return 'appid' in self._values

    @property
    def mch_id(self):
        """
        名称：商户号
        必填：String(32)
        类型：是
        实例值：1900000109
        描述：微信支付分配的商户号
        """
        return self._values.get('mch_id', None)

    @mch_id.setter
    def mch_id(self, mch_id):
        self._values['mch_id'] = mch_id

    def is_mch_id_set(self):
        return 'mch_id' in self._values

    @property
    def time_stamp(self):
        """
        名称：时间戳
        必填：String(10)
        类型：是
        实例值：1414488825
        描述：系统当前时间，定义规则详见时间戳
        """
        return self._values.get('time_stamp', None)

    @time_stamp.setter
    def time_stamp(self, time_stamp):
        self._values['time_stamp'] = time_stamp

    def is_time_stamp_set(self):
        return 'time_stamp' in self._values

    @property
    def nonce_str(self):
        """
        名称：随机字符串
        必填：String(32)
        类型：是
        实例值：5K8264ILTKCH16CQ2502SI8ZNMTM67VS
        描述：随机字符串，不长于32位。推荐随机数生成算法
        """
        return self._values.get('nonce_str', None)

    @nonce_str.setter
    def nonce_str(self, nonce_str):
        self._values['nonce_str'] = nonce_str

    def is_nonce_str_set(self):
        return 'nonce_str' in self._values

    @property
    def product_id(self):
        """
        名称：商品ID
        必填：String(32)
        类型：是
        实例值：88888
        描述：商户定义的商品id 或者订单号
        """
        return self._values.get('product_id', None)

    @product_id.setter
    def product_id(self, product_id):
        self._values['product_id'] = product_id

    def is_product_id_set(self):
        return 'product_id' in self._values
