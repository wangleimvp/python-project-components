#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from urllib import urlencode

import tornado
import tornado.gen
from service_bo.application import ParentHandler
from service_bo.bos.user import UserReqBO
from service_bo.user_service import UserService
from tornado.escape import utf8
from tornado.httpclient import AsyncHTTPClient
from tornado.web import RequestHandler, HTTPError, _time_independent_equals

from commons import jsonutil
from service_bo.account_service import AccountService
from service_bo.bos.account import AccountType
from upload.upload_helper import UploadHelper
from wechat.wechat_builder import WeChatBuilder
from wechat.wechat_helper import WechatHelper
from wechat.wechat_opensdk import WechatOpenSDK, WechatUserInfo

__author__ = 'freeway'


class WeChatAuthorizeHandler(RequestHandler):
    def get(self, *args, **kwargs):
        next = self.get_argument('next', '/')
        url_template = "https://open.weixin.qq.com/connect/oauth2/authorize?%s#wechat_redirect"

        redirect_uri = self.settings.get('site_root') + "/api/weixin/authorize_response?%s" % urlencode(dict(next=next))
        state = self.xsrf_token
        appid = WechatHelper.get_app_id("default")
        url = url_template % urlencode(
            [
                ("appid", appid),
                ("redirect_uri", redirect_uri),
                ("response_type", "code"),
                ("scope", "snsapi_userinfo"),
                ("state", state),
            ]
        )

        self.redirect(url)


class WeChatAuthorizeResponseHandler(ParentHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, *args, **kwargs):
        self.check_state()
        code = self.get_argument("code", None)
        state = self.get_argument("state", None)
        next = self.get_argument("next", None)
        if not state:
            raise HTTPError(403, "'state' argument missing from GET")
        # _, token, _ = self._decode_xsrf_token(state)
        # _, expected_token, _ = self._get_raw_xsrf_token()
        # logging.info("token:%s, expected_token:%s")
        # if not _time_independent_equals(utf8(token), utf8(expected_token)):
        #     raise HTTPError(403, "state cookie does not match GET argument")
        appid = WechatHelper.get_app_id()
        # secret = wechat_config.get("appsecret")

        wechat_open_sdk = WeChatBuilder.get_wechat_open_sdk('default')
        url = wechat_open_sdk.build_access_token_url(code)
        response = yield tornado.gen.Task(AsyncHTTPClient().fetch, url)
        data = jsonutil.json_decode(response.body)

        if data.get("errcode"):
            raise HTTPError(403, data.get("errmsg"))

        account_service = AccountService()
        account = account_service.get_account(data.get("openid"), AccountType.WEIXIN, appid)
        unionid = data.get("unionid", None)
        web_account = account_service.get_account_by_app_id_union_id(WechatHelper.get_app_id('web'), unionid) \
            if account is None and unionid else None

        user = None
        user_req_bo = None
        if account is None:

            if web_account is None:
                # 从来没有开通微信账号登录
                url = wechat_open_sdk.build_user_info_url(data.get("openid"), data.get("access_token"))
                try:
                    response = yield tornado.gen.Task(AsyncHTTPClient().fetch, url)
                    user_data = jsonutil.json_decode(response.body)
                    WechatOpenSDK.check_official_error(user_data)
                except Exception as e:
                    logging.error(e.message)
                    raise HTTPError(403, e.message)
                else:
                    logging.info(user_data)
                    user_info = WechatUserInfo(user_data)
                    gender = 'N'
                    if user_info.sex == 1:
                        gender = 'M'
                    elif user_info.sex == 2:
                        gender = 'F'

                    avatar = ''
                    if user_info.headimgurl and len(user_info.headimgurl) > 0:
                        try:
                            response = yield tornado.gen.Task(AsyncHTTPClient().fetch, user_info.headimgurl)
                            avatar = UploadHelper.upload_image(response.body)
                        except Exception as e:
                            logging.error(e.message)

                    user_req_bo = UserReqBO()
                    user_req_bo.context = self.get_context_bo()
                    user_req_bo.name = user_info.nickname
                    user_req_bo.avatar = avatar
                    user_req_bo.gender = gender
            else:
                user = UserService().get_user(web_account.user_id)

                user_req_bo = UserReqBO()
                user_req_bo.context = self.get_context_bo()
                user_req_bo.context.current_user_id = user.user_id
                user_req_bo.name = user.name
                user_req_bo.avatar = user.avatar
                user_req_bo.gender = user.gender

        oauth_token = account_service.add_weixin_oauth_token(appid,
                                                             data.get("openid"),
                                                             data.get("unionid"),
                                                             data.get("access_token"),
                                                             data.get("refresh_token"),
                                                             data.get("expires_in"),
                                                             data.get("scope"),
                                                             user_req_bo)
        if user is None:
            if account is None:
                account = account_service.get_account(data.get("openid"), AccountType.WEIXIN, appid)
            user_service = UserService()
            user = user_service.get_user(account.user_id)
        if user:
            if not user.is_locked:
                self.current_weixin_token = oauth_token
                self.set_login_token(user)
                self.redirect(next)
        else:
            raise HTTPError(403, 'current user is locked')

    def check_state(self):
        token = self.get_argument("state", None)
        if not token:
            raise HTTPError(403, "'state' argument missing from GET")
        _, token, _ = self._decode_xsrf_token(token)
        _, expected_token, _ = self._get_raw_xsrf_token()
        if not _time_independent_equals(utf8(token), utf8(expected_token)):
            raise HTTPError(403, "XSRF cookie does not match state")
