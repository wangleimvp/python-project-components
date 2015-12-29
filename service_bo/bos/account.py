#!/usr/bin/env python
# -*- coding: utf-8 -*-
from service_bo.base_service import ReqBO
from service_bo.biz_model import BizModel, Attribute
from service_bo.validator import Validators, Required, MinLength, MaxLength, Digits, Equals
from service_bo.bos import COUNTRY_CODE_ATTRIBUTE, VALIDATION_CODE_ATTRIBUTE, PASSWORD_ATTRIBUTE, \
    NEW_MOBILE_ATTRIBUTE, \
    MOBILE_ATTRIBUTE, OLD_PASSWORD_ATTRIBUTE, PASSWORD_VALIDATORS, CAPTCHA_ATTRIBUTE

__author__ = 'freeway'


class AccountBO(BizModel):
    user_id = Attribute(default=None)
    account_type = Attribute(default=None)
    name = Attribute(default=None)


class AccountWeixinBO(BizModel):
    user_id = Attribute(default=None)
    account_type = Attribute(default=None)
    name = Attribute(default=None)
    session_token = Attribute(default=None)
    access_token = Attribute(default=None)
    refresh_token = Attribute(default=None)
    expired_at = Attribute(default=long)
    scope = Attribute(default=None)


class AccountType(object):
    MOBILE = 'mobile'
    WEIXIN = 'weixin'


class OauthTokenBO(BizModel):
    # 账户id
    account_id = Attribute(default=None)
    # 账户类型
    account_type = Attribute(default=None)
    # 微信关于用户的openid
    open_id = Attribute(default=None)
    # 微信关于用户的unionid
    union_id = Attribute(default=None)
    # 会话token 用于保存到cookie中，标识这个用户是关联的哪一个oauth_token的记录
    session_token = Attribute(default=None)
    # 访问token
    access_token = Attribute(default=None)
    # 刷新token
    refresh_token = Attribute(default=None)
    # 权限范围
    scope = Attribute(default=None)
    # 过期时间
    expired_at = Attribute(default=long)


class AuthenticateReqBO(ReqBO):
    # 国家地区编码
    country_code = COUNTRY_CODE_ATTRIBUTE
    # 手机号
    mobile = MOBILE_ATTRIBUTE
    # 密码
    password = PASSWORD_ATTRIBUTE
    # 图片验证码
    captcha = CAPTCHA_ATTRIBUTE
    # oauth_token
    oauth_token = Attribute(default=None, attri_type=OauthTokenBO)


class AccountChangeSendSmsReqBO(ReqBO):
    # 国家地区编码
    country_code = COUNTRY_CODE_ATTRIBUTE
    # 新手机号
    new_mobile = NEW_MOBILE_ATTRIBUTE


class SendSmsReqBO(ReqBO):
    # 国家地区编码
    country_code = COUNTRY_CODE_ATTRIBUTE
    # 新手机号
    mobile = MOBILE_ATTRIBUTE


class AccountChangeReqBO(ReqBO):
    # 国家地区编码
    country_code = COUNTRY_CODE_ATTRIBUTE
    # 新手机号
    new_mobile = NEW_MOBILE_ATTRIBUTE
    # 密码
    password = PASSWORD_ATTRIBUTE
    # 手机验证码
    validation_code = VALIDATION_CODE_ATTRIBUTE


class ChangePasswordReqBO(ReqBO):
    # 老密码
    old_password = OLD_PASSWORD_ATTRIBUTE
    # 新密码
    new_password = Attribute(default='', validators=Validators(PASSWORD_VALIDATORS, name="新密码"))
    # 确认新密码
    new_password_confirm = Attribute(default='',
                                     validators=Validators(
                                         PASSWORD_VALIDATORS + [Equals(field="new_password", field_name="新密码")],
                                         name="确认新密码"))
    # 验证码
    validation_code = VALIDATION_CODE_ATTRIBUTE


class GetByUserIdAccountTypeReqBO(ReqBO):
    account_type = Attribute(default=AccountType.MOBILE)
    app_id = Attribute(default='')


class ResetPasswordReqBO(ReqBO):
    # 国家地区编码
    country_code = COUNTRY_CODE_ATTRIBUTE
    # 新手机号
    mobile = MOBILE_ATTRIBUTE
    # 密码
    password = PASSWORD_ATTRIBUTE
    # 密码确认
    password_confirm = Attribute(default='',
                                 validators=Validators(
                                     PASSWORD_VALIDATORS + [Equals(field="password", field_name="密码")],
                                     name="密码确认"))
    # 手机验证码
    validation_code = VALIDATION_CODE_ATTRIBUTE


class SignupReqBO(ReqBO):
    # 国家地区编码
    country_code = COUNTRY_CODE_ATTRIBUTE
    # 新手机号
    mobile = MOBILE_ATTRIBUTE
    # 密码
    password = PASSWORD_ATTRIBUTE
    # 密码确认
    password_confirm = Attribute(default='',
                                 validators=Validators(
                                     PASSWORD_VALIDATORS + [Equals(field="password", field_name="密码")],
                                     name="密码确认"))
    # 手机验证码
    validation_code = VALIDATION_CODE_ATTRIBUTE

