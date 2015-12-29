#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy

import datetime
from app.services.mq_send_service import MQSendService
from datebase.participant_dao import ParticipantDao
from datebase.party_dao import PartyDao
from datebase.party_ticket_item_dao import PartyTicketItemDao
from datebase.user_dao import UserDao
from datebase.wexin_subscribe_dao import WeixinSubscribeDao

from commons import dateutil
from datebase.account_dao import AccountDao
from datebase.database_builder import DatabaseBuilder
from service_bo.base_service import BaseService
from service_bo.bos.account import AccountType
from wechat.wechat_helper import WechatHelper
from wechat.weixin_template_builder import WeixinTemplateBuilder

__author__ = 'freeway'


class WeChatNoticeService(BaseService):

    def __init__(self):
        self._default_db = DatabaseBuilder.get_default_db_instance()

    def check_in_for_weixin(self, check_in_for_weixin_get_req_bo):
        """

        :param check_in_for_weixin_get_req_bo:
        :type check_in_for_weixin_get_req_bo: app.services.bos.participant.CheckInForWeiXinGetReqBO
        :return:
        :rtype:
        """

        with self.create_session(self._default_db) as session:
            account_dao = AccountDao(session)
            open_id = check_in_for_weixin_get_req_bo.open_id
            app_id = check_in_for_weixin_get_req_bo.app_id
            # open_id
            account_name = open_id
            # 获取微信账号
            account = account_dao.get_by_name_account_type_app_id(account_name,
                                                                  AccountType.WEIXIN,
                                                                  app_id=app_id)
            # 账号不存在
            if account is None:
                return "你扫描了一个无效的签到码"
            # 获取扫码的结果
            paty_id_checkin_code = check_in_for_weixin_get_req_bo.paty_id_checkin_code
            split_parts = str(paty_id_checkin_code).split('|')
            if len(split_parts) != 2:
                return "你扫描了一个无效的签到码"
            party_id, checkin_code = split_parts
            # 获取当前活动
            party_dao = PartyDao(session)
            party = party_dao.get(party_id)
            # 活动不存在
            if party is None:
                return "你扫描了一个无效的签到码"
            # 当前用户与活动组织者不一致,无权操作！
            if account.user_id != party.user_id:
                return "你扫描了一个无效的签到码"
            # 获取报名信息
            participant_dao = ParticipantDao(session)
            user_dao = UserDao(session)
            participant = participant_dao.get_participant_by_party_id_and_checkin_code(party_id, checkin_code)
            # 报名信息不存在
            if participant is None:
                return "你扫描了一个无效的签到码"
            # 该用户已经签到
            if participant.is_checkin:
                return "该用户已经签到！"
            participant.is_checkin = True
            participant_dao.update(participant)
            user = user_dao.get(participant.user_id) if participant.user_id else None
            if user is None:
                return "你扫描了一个无效的签到码"
            party_owner = user_dao.get(party.user_id) if party.user_id else None
            if party_owner is None:
                return "你扫描了一个无效的签到码"
            # 通过MQ给报名人发微信通知
            MQSendService.send_to_participant_for_check_in(participant.party_id, participant.user_id)
            # 给活动组织者回复微信通知
            check_in_party_owner_template_message = WeixinTemplateBuilder.get_template_by_name('check_in_party_owner')
            if check_in_party_owner_template_message:
                participant_dao = ParticipantDao(session)
                check_in_count = participant_dao.get_check_in_count_by_party_id(party_id)
                total_count = participant_dao.count_by_party_id(party_id)
                not_check_in_count = total_count - check_in_count
                params = [user.name, party.title, check_in_count]
                message = check_in_party_owner_template_message.format(*params)
                if not_check_in_count == 0:
                    message += '，全员签到完毕。'
                else:
                    message = message + '，' + str(not_check_in_count) + '人未签到。'
                if participant.charge > 0:
                    ticket_item_dao = PartyTicketItemDao(session)
                    ticket_item = ticket_item_dao.get_by_ticket_item_id_party_id(participant.ticket_item_id, participant.party_id)
                    message += '\n收费项目名称：' + str(ticket_item.name) + '\n项目价格：' + str(ticket_item.price)
            else:
                message = user.name + '在“' + str(party.title) + '”进行了签到!'
            return message

    def send_participant_check_in_message_for_weixin(self, party_id, user_id):
        """ 给报名人发送签到成功的微信公众号通知

        :param user_id:
        :type user_id:
        :return:
        :rtype:
        """
        with self.create_session(self._default_db) as session:
            user_dao = UserDao(session)
            party_dao = PartyDao(session)
            user = user_dao.get(user_id) if user_id else None
            party = party_dao.get(party_id) if party_id else None
            if user is None or party is None:
                return
            participant_open_id, participant_is_subscribed = self.get_open_id_is_subscribed_by_user_id(user_id)
            check_in_participant_template_message = WeixinTemplateBuilder.get_template_by_name('check_in_participant')
            if participant_open_id and participant_is_subscribed and check_in_participant_template_message:
                template_id = check_in_participant_template_message['template_id']
                message = copy.deepcopy(check_in_participant_template_message['data'])
                message['first']['value'] = str(message['first']['value']).format(user.name)
                message['keyword1']['value'] = str(message['keyword1']['value']).format(party.title)
                message['keyword2']['value'] = str(message['keyword2']['value']).format(dateutil.datetime_to_string(datetime.datetime.now(), '%Y-%m-%d %H:%M'))
                message['keyword3']['value'] = str(message['keyword3']['value']).format(party.address)
                message['remark']['value'] = str(message['remark']['value']).format(user.name)
                wechat = WechatHelper.get_wechat_basic()
                wechat.send_template_message(participant_open_id, template_id, message, url=Settings.SITE_ROOT + "/parties/" + party.party_id + "/detail")

    def get_open_id_is_subscribed_by_user_id(self, user_id):
        """ 获取微信的open_id， 还有该用户是否订阅过公众账号

        :param user_id:
        :type user_id:
        :return:
        :rtype:
        """
        with self.create_session(self._default_db) as session:
            app_id = WechatHelper.get_app_id()
            account_dao = AccountDao(session)
            account = account_dao.get_by_user_id_account_type(user_id, AccountType.WEIXIN, app_id)
            if account is None:
                return None, False
            open_id = account.name if account else None
            # 如果被扫码用户未关注公众账号则不发送微信通知
            weixin_num = WechatHelper.get_weixin_num()
            is_subscribed = False
            if weixin_num:
                wexin_subscribe_dao = WeixinSubscribeDao(session)
                wexin_subscribe = wexin_subscribe_dao.get_by_weixin_num_open_id(weixin_num, open_id)
                if wexin_subscribe and wexin_subscribe.is_subscribed:
                    is_subscribed = True
            return open_id, is_subscribed