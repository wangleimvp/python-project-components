#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from urllib import urlencode
import requests
from wechat_sdk.exceptions import OfficialAPIError, ParseError

__author__ = 'freeway'


class WechatToken(object):
    """ 微信token对象

    """

    def __init__(self, result_data):
        self.access_token = result_data.get("access_token", None)
        self.expires_in = result_data.get("expires_in", None)
        self.refresh_token = result_data.get("refresh_token", None)
        self.openid = result_data.get("openid", None)
        self.scope = result_data.get("scope", None)
        self.unionid = result_data.get("unionid", None)


class WechatUserInfo(object):
    """ 微信用户信息

    """

    def __init__(self, result_data):
        self.subscribe = result_data.get("subscribe", None)
        self.openid = result_data.get("openid", None)
        self.nickname = result_data.get("nickname", None)
        self.sex = result_data.get("sex", None)
        self.province = result_data.get("province", None)
        self.city = result_data.get("city", None)
        self.country = result_data.get("country", None)
        self.headimgurl = result_data.get("headimgurl", None)
        self.privilege = result_data.get("privilege", None)
        self.unionid = result_data.get("unionid", None)


class WechatOpenSDK(object):
    """ 微信开放平台Api

    """

    def __init__(self, app_id=None, app_secret=None):
            """
            :param app_id: App ID
            :param app_secret: App Secret
            """
            self.__app_id = app_id
            self.__app_secret = app_secret

    def request_access_token(self, code):
        """ 获取access token

        :param code:
        :return:
        """
        url = self.build_access_token_url(code)
        return WechatToken(self._get(url))

    def request_refresh_token(self, refresh_token):
        """ 刷新token

        :param refresh_token:
        :return:
        """
        url = self.build_refresh_token_url(refresh_token)
        return WechatToken(self._get(url))

    def request_user_info(self, open_id, access_token, lang='zh_CN'):
        """ 用户信息

        :param open_id:
        :param access_token:
        :param lang:
        :return:
        """
        url = self.build_user_info_url(open_id, access_token, lang)
        return WechatUserInfo(self._get(url))

    def request_auth_access_token(self, open_id, access_token):
        """ 验证access_token有效性

        :param open_id:
        :param access_token:
        :return: True有效，False无效
        """
        url = self.build_auth_access_token_url(open_id, access_token)
        result = self._get(url)
        return result and result.get("errcode") == 0

    def build_access_token_url(self, code):
        url = "https://api.weixin.qq.com/sns/oauth2/access_token?" + urlencode(
            [
                ("appid", self.__app_id),
                ("secret", self.__app_secret),
                ("code", code),
                ("grant_type", "authorization_code")
            ]
        )
        return url

    def build_refresh_token_url(self, refresh_token):
        url = "https://api.weixin.qq.com/sns/oauth2/refresh_token?" + urlencode(
            [
                ("appid", self.__app_id),
                ("grant_type", "refresh_token"),
                ("refresh_token", refresh_token)
            ]
        )
        return url

    @staticmethod
    def build_user_info_url(open_id, access_token, lang='zh_CN'):
        url = "https://api.weixin.qq.com/sns/userinfo?" + urlencode(
            [
                ("access_token", access_token),
                ("openid", open_id),
                ("lang", lang)
            ]
        )
        return url

    @staticmethod
    def build_auth_access_token_url(open_id, access_token):
        """ 检验access_token是否有效

        :param access_token:
        :param open_id:
        :return:
        """
        url = "https://api.weixin.qq.com/sns/auth?" + urlencode(
            [
                ("access_token", access_token),
                ("openid", open_id)
            ]
        )
        return url

    @staticmethod
    def check_official_error(json_data):
        """
        检测微信公众平台返回值中是否包含错误的返回码
        :raises OfficialAPIError: 如果返回码提示有错误，抛出异常；否则返回 True
        """
        if "errcode" in json_data and json_data["errcode"] != 0:
            raise OfficialAPIError("{}: {}".format(json_data["errcode"], json_data["errmsg"]))

    def _request(self, method, url, **kwargs):
        """
        向微信服务器发送请求
        :param method: 请求方法
        :param url: 请求地址
        :param kwargs: 附加数据
        :return: 微信服务器响应的 json 数据
        :raise HTTPError: 微信api http 请求失败
        """
        if isinstance(kwargs.get("data", ""), dict):
            body = json.dumps(kwargs["data"], ensure_ascii=False)
            body = body.encode('utf8')
            kwargs["data"] = body

        r = requests.request(
            method=method,
            url=url,
            **kwargs
        )
        r.raise_for_status()
        response_json = r.json()
        self.check_official_error(response_json)
        return response_json

    def _get(self, url, **kwargs):
        """
        使用 GET 方法向微信服务器发出请求
        :param url: 请求地址
        :param kwargs: 附加数据
        :return: 微信服务器响应的 json 数据
        :raise HTTPError: 微信api http 请求失败
        """
        return self._request(
            method="get",
            url=url,
            **kwargs
        )

    def _post(self, url, **kwargs):
        """
        使用 POST 方法向微信服务器发出请求
        :param url: 请求地址
        :param kwargs: 附加数据
        :return: 微信服务器响应的 json 数据
        :raise HTTPError: 微信api http 请求失败
        """
        return self._request(
            method="post",
            url=url,
            **kwargs
        )

    def _transcoding(self, data):
        """
        编码转换
        :param data: 需要转换的数据
        :return: 转换好的数据
        """
        if not data:
            return data

        result = None
        if type(data) == unicode:
            result = data
        elif type(data) == str:
            result = data.decode('utf-8')
        else:
            raise ParseError()
        return result
