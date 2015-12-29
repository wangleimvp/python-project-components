#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
from service_bo.base_service import BaseService
from memcache.memcache_factory import MemCacheFactory


__author__ = 'freeway'


class CaptchaService(BaseService):

    # 小写字母，去除可能干扰的i，l，o，z
    _letter_cases = "abcdefghjkmnprstuvwxy"
    # 大写字母
    _upper_cases = _letter_cases.upper()
    # 数字
    _numbers = ''.join(map(str, range(3, 10)))
    _init_chars = ''.join((_letter_cases, _upper_cases, _numbers))
    _cache_session = 'captcha'

    @classmethod
    def _parse_to_key(cls, account_name):
        return "captcha:{0}".format(account_name)

    @classmethod
    def generate_captcha_by_mobile(cls, country_code, mobile):
        """生成验证码

        :param country_code: 手机国家码
        :param mobile: 手机号
        :return:
        """
        account_name = '-'.join([country_code, mobile])
        return cls.generate_captcha(account_name)

    @classmethod
    def generate_captcha(cls, account_name):
        """ 生成验证吗

        :param account_name: 用户账号
        :return:
        """
        captcha = ''.join(random.sample(cls._init_chars, 4))
        cache_factory = MemCacheFactory.get_instance(cls._cache_session)
        key = cls._parse_to_key(account_name)
        cache_factory.set(key, captcha)
        return captcha

    @classmethod
    def validate_captcha_by_mobile(cls, country_code, mobile, captcha):
        """ 验证码验证

        :param country_code:
        :param mobile:
        :param captcha: str 需要校验的验证码
        :return:
        """
        return cls.validate_captcha('-'.join([country_code, mobile]), captcha)

    @classmethod
    def validate_captcha(cls, account_name, captcha):
        """ 验证码验证

        :param account_name: 用户账号
        :param captcha: 验证码
        :return:
        """
        cache_factory = MemCacheFactory.get_instance(cls._cache_session)
        key = cls._parse_to_key(account_name)
        cached_captcha = cache_factory.get(key)
        if cached_captcha is None:
            return False
        is_validate = str(captcha).upper() == str(cached_captcha).upper()
        # 一旦校验完成就将这个验证码删除掉
        cache_factory.delete(key)
        return is_validate