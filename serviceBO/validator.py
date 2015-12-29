#!/usr/bin/env python
# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
import inspect
import re

__author__ = 'freeway'


def _isstr(s):
    """
    Python 2/3 compatible check to see
    if an object is a string type.

    """

    try:
        return isinstance(s, basestring)
    except NameError:
        return isinstance(s, str)


class Validator(object):
    """
    Abstract class that advanced
    validators can inherit from in order
    to set custom error messages and such.

    """

    __metaclass__ = ABCMeta

    message = "验证失败"

    @abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplemented


class In(Validator):
    """
    Use to specify that the
    value of the key being
    validated must exist
    within the collection
    passed to this validator.

    # Example:
        validations = {
            "field": [In([1, 2, 3])]
        }
        passes = {"field":1}
        fails  = {"field":4}

    """

    def __init__(self, collection=None, message=None):
        """

        :param collection:
        :type collection: list
        :param message:
        :type message: str|unicode
        :return:
        :rtype:
        """
        self.priority = 3
        self.collection = collection
        self.message = "必须是{0}其中的一个值".format(collection) if message is None else message

    def __call__(self, value):
        return value in self.collection


class Required(Validator):
    def __init__(self, message=None):
        """

        :param collection:
        :type collection: list
        :param message:
        :type message: str
        :return:
        :rtype:
        """
        self.priority = 0
        self.message = "不能为空" if message is None else message

    def __call__(self, value):
        return value is not None and len(str(value).strip()) > 0


class MaxLength(Validator):
    def __init__(self, length=None, message=None):
        """

        :param length:
        :type length: int|float
        :param message:
        :type message: dict
        :return:
        :rtype:
        """
        self.priority = 3
        self.length = length
        self.message = "不能大于{0}个字符".format(length) if message is None else message

    def __call__(self, value):
        return len(str(value)) <= self.length


class MinLength(Validator):
    def __init__(self, length=None, message=None):
        """

        :param length:
        :type length: int|float
        :param message:
        :type message: dict
        :return:
        :rtype:
        """
        self.priority = 3
        self.length = length
        self.message = "不能小于{0}个字符".format(length) if message is None else message

    def __call__(self, value):
        return len(str(value)) >= self.length


class Max(Validator):
    def __init__(self, value=None, field=None, message=None):
        """

        :param value:
        :type value: int|float
        :param message:
        :type message: dict
        :return:
        :rtype:
        """
        self.priority = 3
        self.field = field
        self.value = value
        self.message = "不能大于{0}".format(value) if message is None else message

    def __call__(self, value, field_value):
        return value <= self.value if self.field is None else value <= field_value


class Min(Validator):
    def __init__(self, value=None, field=None, message=None):
        """

        :param value:
        :type value: int|float
        :param message:
        :type message: dict
        :return:
        :rtype:
        """
        self.priority = 3
        self.value = value
        self.field = field
        self.message = "不能小于{0}".format(value) if message is None else message

    def __call__(self, value, field_value):
        return value >= self.value if self.field is None else value >= field_value


class Email(Validator):
    # A valid email address.
    VALID_EMAIL = '^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$'

    def __init__(self, message=None):
        """

        :param message:
        :type message: dict
        :return:
        :rtype:
        """
        self.priority = 3
        self.regexp = Email.VALID_EMAIL
        self.message = "无效的电子邮箱格式" if message is None else message

    def __call__(self, value):
        return None != re.search(self.VALID_EMAIL, value)


class Regexp(Validator):
    def __init__(self, regexp=None, message=None):
        """

        :param value:
        :type value: int|float
        :param message:
        :type message: dict
        :return:
        :rtype:
        """
        self.priority = 3
        self.regexp = regexp
        self.message = "数据格式无效" if message is None else message

    def __call__(self, value):
        return None != re.search(self.regexp, value)


class Digits(Validator):
    VALID_DIGITS = '^\d+$'

    def __init__(self, message=None):
        """

        :param message:
        :type message: dict
        :return:
        :rtype:
        """
        self.priority = 2
        self.regexp = Digits.VALID_DIGITS
        self.message = "必须是整数" if message is None else message

    def __call__(self, value):
        return None != re.search(self.VALID_DIGITS, value)


class Number(Validator):
    VALID_NUMBER = '^[-+]?\d*\\.?\d*$'

    def __init__(self, message=None):
        """

        :param value:
        :type value: int|float
        :param message:
        :type message: dict
        :return:
        :rtype:
        """
        self.priority = 2
        self.regexp = Number.VALID_NUMBER
        self.message = "必须是数字" if message is None else message

    def __call__(self, value):
        return None != re.search(self.VALID_NUMBER, value)


class Date(Validator):
    VALID_DATE_ISO = '^\d{4}[-]\d{1,2}[-]\d{1,2}$'

    def __init__(self, message=None):
        """

        :param value:
        :type value: int|float
        :param message:
        :type message: dict
        :return:
        :rtype:
        """
        self.priority = 3
        self.regexp = Date.VALID_DATE_ISO
        self.message = "无效日期格式" if message is None else message

    def __call__(self, value):
        return None != re.search(self.VALID_DATE_ISO, value)


class Url(Validator):
    VALID_URL = '''^(http(s)?://([a-zA-Z0-9]+.)(\S*?\.\S*?))(\s|\|\)|\]|\[|\{|\}|,|\"|\'|:|\<||\.\s)$'''

    def __init__(self, message=None):
        """

        :param value:
        :type value: int|float
        :param message:
        :type message: dict
        :return:
        :rtype:
        """
        self.priority = 3
        self.regexp = Url.VALID_URL
        self.message = "无效的网站链接" if message is None else message

    def __call__(self, value):
        return None != re.search(self.VALID_URL, value)


class Mobile(Validator):
    VALID_MOBILE = '''^1[1-9]\d{9}$'''

    def __init__(self, message=None):
        """

        :param message:
        :type message: dict
        :return:
        :rtype:
        """
        self.priority = 4
        self.regexp = Mobile.VALID_MOBILE
        self.message = "无效的手机号" if message is None else message

    def __call__(self, value):
        return None != re.search(self.VALID_MOBILE, value)


class ASCII(Validator):
    VALID_IS_ASCII = '^[\x00-\x7f]*$'

    def __init__(self, message=None):
        """

        :param value:
        :type value: int|float
        :param message:
        :type message: dict
        :return:
        :rtype:
        """
        self.priority = 3
        self.regexp = ASCII.VALID_IS_ASCII
        self.message = "存在无效的字符" if message is None else message

    def __call__(self, value):
        return None != re.search(self.VALID_IS_ASCII, value)


class Password(ASCII):
    pass


class Equals(Validator):
    def __init__(self, value=None, field=None, field_name=None, message=None):
        """

        :param value:
        :type value:
        :param field:
        :type field:
        :param field_name:
        :type field_name:
        :param message:
        :type message:
        :return:
        :rtype:
        """
        self.priority = 2
        self.value = value
        self.field = field
        self.field_name = field_name
        if field_name:
            self.message = "和“{0}”内容必须一致".format(field_name) if message is None else message
        else:
            self.message = "内容必须是{0}".format(value) if message is None else message

    def __call__(self, value, field_value):
        return value == field_value if self.field else value == self.value


class RequiredForFieldIsEmpty(Validator):
    def __init__(self, field=None, message=None):
        """

        :param field:
        :type field:
        :param field_name:
        :type field_name:
        :param message:
        :type message:
        :return:
        :rtype:
        """
        self.priority = 0
        self.field = field
        self.message = "不能为空" if message is None else message

    def __call__(self, value, field_value):
        return True if field_value is not None and len(str(field_value).strip()) > 0 else\
            value is not None and len(str(value).strip()) > 0


class Validators(object):
    __metaclass__ = ABCMeta

    def __init__(self, validators, name=None):
        """

        :param validators:
        :type validators: list
        :param name:
        :type name:
        :return:
        :rtype:
        """
        self.name = name
        self.validators = list(validators)
        self.validators.sort(key=lambda x: x.priority)


if __name__ == "__main__":

    required = Required()
    print required("ss")

    abc = RequiredForFieldIsEmpty("image")
    print "abc:" + str(abc("", None))

    date = Date()
    print date("2004-12-12")
    print date("2004/12/12")
    print date.message
    print date.__class__.__name__
    print dir(date)
    print inspect.getmembers(date)