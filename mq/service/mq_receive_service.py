#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from service_bo.my_party_service import MyPartyService
from service_bo.party_time_line_service import PartyTimeLineService

from commons import jsonutil, stringutil
from service_bo.base_service import BaseService
from wechat.wechat_notice_service import WeChatNoticeService

__author__ = 'freeway'


class MQReceiveService(BaseService):

    @staticmethod
    def add_party_callback(body):
        """

        :param ch:
        :param method:
        :param properties:
        :param body:
        :return:
        """
        logging.info("message:%r" % body)
        data = jsonutil.json_decode(body)
        title = data.get('title')
        tips = data.get('tips')
        cover_img = data.get('cover_img')
        party_id = data.get('party_id')
        party_owner_id = data.get('party_owner_id')

        if stringutil.is_blank(title) or \
                stringutil.is_blank(party_id) or \
                stringutil.is_blank(party_owner_id):
            return

        party_time_line_service = PartyTimeLineService()
        my_party_service = MyPartyService()
        party_time_line_service.add(party_id, party_owner_id, party_owner_id, title, tips, cover_img)
        my_party_service.add(party_id, party_owner_id)
        wechat_notice_service = WeChatNoticeService()
        wechat_notice_service.send_add_update_party_msg_to_staff(party_id, is_add=True)
