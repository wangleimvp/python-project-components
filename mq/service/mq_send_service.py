#!/usr/bin/env python
# -*- coding: utf-8 -*-
from commons import jsonutil
from service_bo.base_service import BaseService
from mq.configs.mq_builder import MQBuilder

__author__ = 'freeway'


class QueueName(object):

    JOIN_PARTY = 'join_party'


class PubName(object):

    WEB_SOCKET = 'web_socket'


class MQSendService(BaseService):

    @classmethod
    def _send_for_party(cls, queue_name, json_str):
        """ 发送通知

        :param queue_name:
        :param json_str:
        :return:
        """
        client = MQBuilder.get_mq_client_by_name('default')
        client.send(queue_name, json_str)

    @classmethod
    def send_for_join_party(cls, party_id, party_owner_id, user_id, user_name, title, cover_img):
        """ 发送活动通知

        :param party_id:
        :param party_owner_id:
        :param user_id:
        :param user_name:
        :param title:
        :param cover_img:
        :return:
        """
        cls._send_for_party(QueueName.JOIN_PARTY,
                            jsonutil.json_encode(dict(title=title,
                                                      party_id=party_id,
                                                      party_owner_id=party_owner_id,
                                                      user_id=user_id,
                                                      user_name=user_name,
                                                      cover_img=cover_img)))
