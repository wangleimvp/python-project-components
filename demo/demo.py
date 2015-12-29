#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from service_bo.application import BaseHandler, authenticated, RestfulAPIHandler
from service_bo.weixin_subscribe_service import WeixinSubscribeService
from tornado.web import StaticFileHandler, HTTPError

from service_bo.account_service import AccountService
from service_bo.base_service import ServiceValidationFailsException
from service_bo.bos.account import GetByUserIdAccountTypeReqBO, AccountType
from service_bo.view_model import ViewModel
from wechat.wechat_helper import WechatHelper
from wechat.wechat_opensdk import WechatUserInfo

__author__ = 'wanglei'


class HtmlDemoHandler(BaseHandler):
    """获取用户参加的活动列表信息

    """

    @authenticated
    def get(self, html_path, html_name, *args, **kwargs):
        """处理查询请求

        """
        result = ViewModel()
        self.render(str(html_path) + '/' + str(html_name) + '.html', **result)


class ResetStaticUrl(RestfulAPIHandler):

    def get(self, *args, **kwargs):

        self.require_setting("static_path", "static_url")
        template_path = self.get_template_path()
        if not template_path:
            raise ServiceValidationFailsException("You must define the 'template_path' setting in your application")
        with self._template_loader_lock:
            for loader in self._template_loaders.values():
                loader.reset()
        StaticFileHandler.reset()
        self.write('success')


class WechatSubscribe(RestfulAPIHandler):

    def get(self, *args, **kwargs):

        app_id = WechatHelper.get_app_id()
        weixin_num = WechatHelper.get_weixin_num()
        wechat = WechatHelper.get_wechat_basic()
        account_service = AccountService()
        get_by_account_type_req_bo = GetByUserIdAccountTypeReqBO()
        get_by_account_type_req_bo.account_type = AccountType.WEIXIN
        get_by_account_type_req_bo.app_id = app_id
        accounts = account_service.gets_by_account_type(get_by_account_type_req_bo)
        subscribe_service = WeixinSubscribeService()

        update_num = 0
        for start_index in range(0, len(accounts), 100):
            end_index = start_index + 100
            accounts_temp = accounts[start_index:end_index]
            update_num += len(accounts_temp)
            try:
                user_info_list = self.get_user_info_list(wechat, accounts_temp)['user_info_list']
            except Exception as e:
                logging.error(e.message)
                raise HTTPError(403, e.message)
            else:
                for user_info in user_info_list:
                    user_info = WechatUserInfo(user_info)
                    subscribe_service.update_subscribe(weixin_num, user_info.openid, user_info.subscribe)
            logging.info('updated weixin_subscribe table data num:' + str(update_num))
        logging.info('update weixin_subscribe table finished')
        self.write('success')

    @staticmethod
    def get_user_info_list(wechat, accounts, lang='zh_CN'):
        """
        获取用户基本信息
        详情请参考 http://mp.weixin.qq.com/wiki/14/bb5031008f1494a59c6f71fa0f319c66.html
        :param user_id: 用户 ID, 就是你收到的 WechatMessage 的 source
        :param lang: 返回国家地区语言版本，zh_CN 简体，zh_TW 繁体，en 英语
        :return: 返回的 JSON 数据包
        :raise HTTPError: 微信api http 请求失败
        """
        wechat._check_appid_appsecret()
        user_list = []
        for account in accounts:
            temp_dict = dict()
            open_id = account.name
            temp_dict['openid'] = open_id
            temp_dict['lang'] = lang
            user_list.append(temp_dict)
        return wechat._post(
            url='https://api.weixin.qq.com/cgi-bin/user/info/batchget',
            params={
                'access_token': wechat.access_token
            },
            data={
                'user_list': user_list,
            }
        )