#!/usr/bin/env python
# -*- coding: utf-8 -*-
from service_bo.biz_model import Attribute
from service_bo.validator import Validators, MinLength, MaxLength, Digits, Password, Mobile
from service_bo.validator import Required

__author__ = 'freeway'

COUNTRY_CODE_ATTRIBUTE = Attribute(default='86', validators=Validators([
    Required(), MinLength(length=1), MaxLength(length=4), Digits()
], name="国家/地区编码"))

VALIDATION_CODE_ATTRIBUTE = Attribute(default='', validators=Validators([
    Required(message="必须是6位数字"), MinLength(length=6), MaxLength(length=6), Digits()
], name="验证码"))

MOBILE_ATTRIBUTE = Attribute(default='', validators=Validators([
    Required(), MaxLength(length=11), Mobile()
], name="手机号"))

NEW_MOBILE_ATTRIBUTE = Attribute(default='', validators=Validators([
    Required(), MaxLength(length=11), Mobile()
], name="新手机号"))

PASSWORD_VALIDATORS = [
    Required(), MinLength(length=6), MaxLength(length=60), Password()
]

PASSWORD_ATTRIBUTE = Attribute(default='', validators=Validators(PASSWORD_VALIDATORS, name="密码"))

OLD_PASSWORD_ATTRIBUTE = Attribute(default='', validators=Validators(PASSWORD_VALIDATORS, name="旧密码"))

CAPTCHA_ATTRIBUTE = Attribute(default='', validators=Validators([
    MaxLength(length=4)
], name="验证码"))
