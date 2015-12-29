#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
import datetime
from decorated.base.dict import DefaultDict

from app.commons import dateutil
from app.commons.base_service import BaseService
from app.commons.dateutil import timestamp
from app.daos.account_dao import AccountDao
from app.daos.participant_dao import ParticipantDao
from app.daos.party_dao import PartyDao
from app.daos.party_post_dao import PartyPostDao
from app.daos.party_ticket_item_dao import PartyTicketItemDao
from app.daos.user_dao import UserDao
from app.daos.wexin_subscribe_dao import WeixinSubscribeDao
from app.handlers.widgets.party import get_party_time
from app.helpers.wechat_helper import WechatHelper
from app.services.bos.account import AccountType
from app.services.mq_send_service import MQSendService
from configs.database_builder import DatabaseBuilder
from configs.settings import Settings
from configs.wechat_builder import WeChatBuilder
from configs.weixin_template_builder import WeixinTemplateBuilder


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

    def send_check_in_message_for_weixin(self, party_id, user_id):
        """ 签到操作的时候要给报名人和活动所属人发送微信通知

        :param user_id:
        :type user_id:
        :return:
        :rtype:
        """
        # 给被扫码的用户发通知
        with self.create_session(self._default_db) as session:
            user_dao = UserDao(session)
            party_dao = PartyDao(session)
            user = user_dao.get(user_id) if user_id else None
            party = party_dao.get(party_id) if party_id else None
            if user is None or party is None:
                return
            party_owner = user_dao.get(party.user_id) if party.user_id else None
            if party_owner is None:
                return
            wechat = WechatHelper.get_wechat_basic()
            # 给活动组织人发送微信通知
            party_owner_open_id, party_owner_is_subscribed = self.get_open_id_is_subscribed_by_user_id(party.user_id)
            check_in_party_owner_template_message = WeixinTemplateBuilder.get_template_by_name('check_in_party_owner')
            if party_owner_open_id and party_owner_is_subscribed and check_in_party_owner_template_message:
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
                participant_dao = ParticipantDao(session)
                participant = participant_dao.get_by_user_id_and_party_id(user_id, party_id)
                if participant.charge > 0:
                    ticket_item_dao = PartyTicketItemDao(session)
                    ticket_item = ticket_item_dao.get_by_ticket_item_id_party_id(participant.ticket_item_id, participant.party_id)
                    message += '\n收费项目名称：' + str(ticket_item.name) + '\n项目价格：' + str(ticket_item.price)
                wechat.send_text_message(party_owner_open_id, message)
            # 给报名人发送微信通知
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
                wechat.send_template_message(participant_open_id, template_id, message, url=Settings.SITE_ROOT + "/parties/" + party.party_id + "/detail")

    def send_join_party_message_for_weixin(self, party_id, user_id):
        """ 参加活动的时候给活动组织者发送微信通知

        :param party_id:
        :type party_id:
        :param user_id:
        :type user_id:
        :return:
        :rtype:
        """
        with self.create_session(self._default_db) as session:
            user_dao = UserDao(session)
            party_dao = PartyDao(session)
            participant_dao = ParticipantDao(session)
            party = party_dao.get(party_id) if party_id else None
            user = user_dao.get(user_id) if user_id else None
            participant = participant_dao.get_by_user_id_and_party_id(user_id, party_id)
            if user is None or party is None or participant is None:
                return
            party_owner = user_dao.get(party.user_id) if party.user_id else None
            if party_owner is None:
                return

            custom_items_str = ''
            # 单位
            if participant.unit:
                custom_items_str = custom_items_str + '\n' + '单位： ' + str(participant.unit) if custom_items_str else '单位： ' + str(participant.unit)
            # 职位
            if participant.position:
                custom_items_str = custom_items_str + '\n' + '职位： ' + str(participant.position) if custom_items_str else '职位： ' + str(participant.position)
            # 行业
            if participant.industry:
                custom_items_str = custom_items_str + '\n' + '行业： ' + str(participant.industry) if custom_items_str else '行业： ' + str(participant.industry)
            # 备注
            if participant.remark:
                custom_items_str = custom_items_str + '\n' + '备注： ' + str(participant.remark) if custom_items_str else '备注： ' + str(participant.remark)
            # 报名人的其他报名信息
            custom_item_list = []
            if party.custom_items:
                party_custom_items = party.custom_items.split(',')
                participant_custom_item_contents = participant.custom_item_contents.split(',')
                custom_items = zip(party_custom_items, participant_custom_item_contents)
                for custom_item in custom_items:
                    custom_item_list.append('： '.join(custom_item))
                custom_items_str = custom_items_str + '\n' + '\n'.join(custom_item_list) if custom_items_str else '\n'.join(custom_item_list)

            # 活动组织人是否订阅该公众号
            open_id, is_subscribed = self.get_open_id_is_subscribed_by_user_id(party.user_id)
            join_party_template_message = WeixinTemplateBuilder.get_template_by_name('join_party_to_party_owner')
            if open_id and is_subscribed and join_party_template_message:
                template_id = join_party_template_message['template_id']
                message = copy.deepcopy(join_party_template_message['data'])
                message['keyword1']['value'] = str(message['keyword1']['value']).format(party.title)
                message['keyword2']['value'] = str(message['keyword2']['value']).format(user.name)
                message['keyword3']['value'] = str(message['keyword3']['value']).format(participant.mobile if participant.mobile else '无')
                message['remark']['value'] = str(message['remark']['value']).format(custom_items_str)
                wechat = WechatHelper.get_wechat_basic()
                wechat.send_template_message(open_id, template_id, message, url=Settings.SITE_ROOT + "/parties/" + party.party_id + "/participants")

            # 给活动报名人发送报名成功通知
            open_id, is_subscribed = self.get_open_id_is_subscribed_by_user_id(user_id)
            join_party_template_message = WeixinTemplateBuilder.get_template_by_name('join_party_to_participant')
            if open_id and is_subscribed and join_party_template_message:
                format_str = '%Y-%m-%d %H:%M'
                if party.end_time:
                    party_time = get_party_time(party.start_time, party.end_time)
                else:
                    party_time = dateutil.datetime_to_string(party.start_time, format_str)
                template_id = join_party_template_message['template_id']
                message = copy.deepcopy(join_party_template_message['data'])
                message['keynote1']['value'] = str(message['keynote1']['value']).format(party.title)
                message['keynote2']['value'] = str(message['keynote2']['value']).format(party_time)
                message['keynote3']['value'] = str(message['keynote3']['value']).format(party.address)
                message['remark']['value'] = str(message['remark']['value']).format('')
                wechat = WechatHelper.get_wechat_basic()
                wechat.send_template_message(open_id, template_id, message, url=Settings.SITE_ROOT + "/parties/" + party.party_id + "/detail")

    def send_quit_party_message_for_weixin(self, party_id, user_id, reason):
        """ 退出活动的时候给活动组织者发送微信通知

        :param party_id:
        :type party_id:
        :return:
        :rtype:
        """
        with self.create_session(self._default_db) as session:
            user_dao = UserDao(session)
            party_dao = PartyDao(session)
            participant_dao = ParticipantDao(session)
            party = party_dao.get(party_id) if party_id else None
            user = user_dao.get(user_id) if user_id else None
            participant = participant_dao.get_by_user_id_and_party_id(user_id, party_id, has_state=False)
            if user is None or party is None or participant is None:
                return
            party_owner = user_dao.get(party.user_id) if party.user_id else None
            if party_owner is None or party is None:
                return
            # 活动组织人是否订阅该公众号
            open_id, is_subscribed = self.get_open_id_is_subscribed_by_user_id(party.user_id)
            quit_party_template_message = WeixinTemplateBuilder.get_template_by_name('quit_party')
            if open_id and is_subscribed and quit_party_template_message:
                message = copy.deepcopy(quit_party_template_message['data'])
                url = Settings.SITE_ROOT + "/parties/" + party.party_id + "/participants"
                if participant and participant.charge > 0:
                    if reason:
                        reason += '\n点击详情，进行拒绝报名操作即可退还报名费'
                    else:
                        reason = '点击详情，进行拒绝报名操作即可退还报名费'
                    url = Settings.SITE_ROOT + "/participants/" + str(participant.id) + "/detail"
                    message['keyword3']['color'] = '#FF0000'
                template_id = quit_party_template_message['template_id']
                message['keyword1']['value'] = str(message['keyword1']['value']).format(party.title)
                message['keyword2']['value'] = str(message['keyword2']['value']).format(user.name)
                message['keyword3']['value'] = str(message['keyword3']['value']).format(reason if reason else '无')
                wechat = WechatHelper.get_wechat_basic()
                wechat.send_template_message(open_id, template_id, message, url=url)

    def send_reject_participant_message_for_weixin(self, party_id, user_id, reject_reason=''):
        """ 拒绝报名的时候微信通知活动报名人

        :param party_id:
        :type party_id:
        :param user_id:
        :type user_id:
        :return:
        :rtype:
        """
        with self.create_session(self._default_db) as session:
            user_dao = UserDao(session)
            party_dao = PartyDao(session)
            participant_dao = ParticipantDao(session)
            party = party_dao.get(party_id) if party_id else None
            user = user_dao.get(user_id) if user_id else None
            participant = participant_dao.get_by_user_id_and_party_id(user_id, party_id, has_state=False)
            if user is None or party is None or participant is None:
                return
            # 活动报名人是否订阅该公众号
            open_id, is_subscribed = self.get_open_id_is_subscribed_by_user_id(user_id)
            reject_participant_template_message = WeixinTemplateBuilder.get_template_by_name('reject_participant')
            if reject_reason and len(reject_reason) != 0:
                reject_participant_template_message += '\n拒绝原因:' + str(reject_reason)
            if participant.charge > 0:
                reject_participant_template_message += '\n您的报名费稍后会通过微信退款'
            if open_id and is_subscribed and reject_participant_template_message:
                reject_participant_template_message = reject_participant_template_message.format(party.title)
                wechat = WechatHelper.get_wechat_basic()
                wechat.send_text_message(open_id, reject_participant_template_message)

    def send_add_comment_message_for_weixin(self, party_id, sender_id, user_id, is_reply=False):
        """ 拒绝报名的时候微信通知活动报名人

        :param sender_id:
        :type sender_id:
        :param user_id:
        :type user_id:
        :param is_reply:
        :type is_reply:
        :return:
        :rtype:
        """
        with self.create_session(self._default_db) as session:
            user_dao = UserDao(session)
            party_dao = PartyDao(session)
            user = user_dao.get(user_id) if user_id else None
            sender = user_dao.get(sender_id) if sender_id else None
            party = party_dao.get(party_id) if party_id else None
            if user is None or sender is None or party is None:
                return
            # 收到评论的人是否订阅该公众号
            open_id, is_subscribed = self.get_open_id_is_subscribed_by_user_id(user_id)
            if is_reply:
                add_comment_template_message = WeixinTemplateBuilder.get_template_by_name('reply_comment')
            else:
                add_comment_template_message = WeixinTemplateBuilder.get_template_by_name('add_comment')
            if open_id and is_subscribed and add_comment_template_message:
                add_comment_template_message = add_comment_template_message.format(sender.name, '\n' + Settings.SITE_ROOT + "/parties/" + party.party_id + "/detail")
                wechat = WechatHelper.get_wechat_basic()
                wechat.send_text_message(open_id, add_comment_template_message)

    def send_change_party_time_message_for_weixin(self, party_id):
        """ 活动时间变化发送微信公众号消息提醒

        :param party_id:
        :type party_id:
        :return:
        :rtype:
        """
        with self.create_session(self._default_db) as session:
            user_dao = UserDao(session)
            party_dao = PartyDao(session)
            party = party_dao.get(party_id) if party_id else None
            if party is None:
                return
            party_owner = user_dao.get(party.user_id) if party.user_id else None
            if party_owner is None or party is None:
                return
            participant_dao = ParticipantDao(session)
            participants = participant_dao.gets_all_by_party_id(party_id)
            user_ids = [participant.user_id for participant in participants]
            # 活动组织人是否订阅该公众号
            for user_id in user_ids:
                user = user_dao.get(user_id) if user_id else None
                if user is None:
                    continue
                open_id, is_subscribed = self.get_open_id_is_subscribed_by_user_id(user_id)
                change_party_time_template_message = WeixinTemplateBuilder.get_template_by_name('change_party_time')
                if open_id and is_subscribed and change_party_time_template_message:
                    format_str = '%Y-%m-%d %H:%M'
                    if party.end_time:
                        party_time = get_party_time(party.start_time, party.end_time)
                    else:
                        party_time = dateutil.datetime_to_string(party.start_time, format_str)
                    template_id = change_party_time_template_message['template_id']
                    message = copy.deepcopy(change_party_time_template_message['data'])
                    message['keyword1']['value'] = str(message['keyword1']['value']).format(party.title)
                    message['keyword2']['value'] = str(message['keyword2']['value']).format(party_time)
                    wechat = WechatHelper.get_wechat_basic()
                    wechat.send_template_message(open_id, template_id, message, url=Settings.SITE_ROOT + "/parties/" + party.party_id + "/detail")

    def send_change_party_address_message_for_weixin(self, party_id):
        """ 活动时间变化发送微信公众号消息提醒

        :param party_id:
        :type party_id:
        :return:
        :rtype:
        """
        with self.create_session(self._default_db) as session:
            user_dao = UserDao(session)
            party_dao = PartyDao(session)
            party = party_dao.get(party_id) if party_id else None
            if party is None:
                return
            party_owner = user_dao.get(party.user_id) if party.user_id else None
            if party_owner is None or party is None:
                return
            participant_dao = ParticipantDao(session)
            participants = participant_dao.gets_all_by_party_id(party_id)
            user_ids = [participant.user_id for participant in participants]
            # 活动组织人是否订阅该公众号
            for user_id in user_ids:
                user = user_dao.get(user_id) if user_id else None
                if user is None:
                    continue
                open_id, is_subscribed = self.get_open_id_is_subscribed_by_user_id(user_id)
                change_party_address_template_message = WeixinTemplateBuilder.get_template_by_name('change_party_address')
                if open_id and is_subscribed and change_party_address_template_message:
                    template_id = change_party_address_template_message['template_id']
                    message = copy.deepcopy(change_party_address_template_message['data'])
                    message['keyword1']['value'] = str(message['keyword1']['value']).format(party.title)
                    message['keyword2']['value'] = str(message['keyword2']['value']).format(party.address)
                    wechat = WechatHelper.get_wechat_basic()
                    wechat.send_template_message(open_id, template_id, message, url=Settings.SITE_ROOT + "/parties/" + party.party_id + "/detail")

    def send_add_update_party_msg_to_staff(self, party_id, is_add=False):
        """

        :param party_id:
        :param is_add:
        :return:
        """
        with self.create_session(self._default_db) as session:
            party_dao = PartyDao(session)
            party = party_dao.get(party_id) if party_id else None
            if party is None:
                return
            user_id = 'E'
            open_id, is_subscribed = self.get_open_id_is_subscribed_by_user_id(user_id)
            if open_id and is_subscribed:
                wechat = WechatHelper.get_wechat_basic()
                if is_add:
                    message = '有用户发布了活动：“' + str(party.title) + '”，请尽快审核'
                else:
                    message = '有用户修改了活动：“' + str(party.title) + '”，请尽快审核'
                wechat.send_text_message(open_id, message)

    def send_party_start_message_for_weixin(self, party_id, user_ids):
        """ 活动开始前发送微信公众号消息提醒

        :param party_id:
        :type party_id:
        :param user_id:
        :type user_id:
        :return:
        :rtype:
        """
        with self.create_session(self._default_db) as session:
            user_dao = UserDao(session)
            party_dao = PartyDao(session)
            party = party_dao.get(party_id) if party_id else None
            if party is None:
                return
            party_owner = user_dao.get(party.user_id) if party.user_id else None
            if party_owner is None:
                return
            for user_id in user_ids:
                user = user_dao.get(user_id) if user_id else None
                if user is None:
                    continue
                # 活动组织人是否订阅该公众号
                open_id, is_subscribed = self.get_open_id_is_subscribed_by_user_id(user_id)
                quit_party_template_message = WeixinTemplateBuilder.get_template_by_name('party_start')
                if open_id and is_subscribed and quit_party_template_message:
                    template_id = quit_party_template_message['template_id']
                    message = copy.deepcopy(quit_party_template_message['data'])
                    message['keyword1']['value'] = str(message['keyword1']['value']).format(user.name)
                    message['keyword2']['value'] = str(message['keyword2']['value']).format(party.title)
                    message['keyword3']['value'] = str(message['keyword3']['value']).format(party.created_at)
                    message['keyword3']['value'] = str(message['keyword4']['value']).format(party.address)
                    wechat = WechatHelper.get_wechat_basic()
                    wechat.send_template_message(open_id, template_id, message, url=Settings.SITE_ROOT + "/parties/" + party.party_id + "/detail")

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

    def party_crontab_for_weixin(self):
        """ 定时检测party数据，在活动开始的是三个小时前给参与的人发送微信通知

        :return:
        :rtype:
        """

        with self.create_session(self._default_db) as session:
            party_dao = PartyDao(session)
            participant_dao = ParticipantDao(session)
            parties = party_dao.gets_for_crontab()
            party_ids = [party.party_id for party in parties]
            participants = participant_dao.gets_by_party_ids(party_ids)
            party_id_user_ids = DefaultDict()
            for participant in participants:
                if party_id_user_ids[participant.party_id]:
                    party_id_user_ids[participant.party_id].append(participant.user_id)
                else:
                    party_id_user_ids[participant.party_id] = [participant.user_id]
            for party_id, user_ids in party_id_user_ids.items():
                self.send_party_start_message_for_weixin(party_id, user_ids)
            return party_ids


if __name__ == '__main__':

    ser = WeChatNoticeService()
    parties_1 = ser.party_crontab_for_weixin()