#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import yaml

from mq.common.mq_client import MQClient

__author__ = 'freeway'


class MQBuilder(object):

    _mqs_config = None
    _clients = {}
    run_mode = None

    @classmethod
    def get_mq_client_by_name(cls, name):
        """

        :param name:
        :type name:
        :return:
        :rtype: app.commons.mq.mq_client.MQClient
        """
        if cls._mqs_config is None:
            with file(os.path.join(os.getcwd(), 'mq_config.yaml'), 'r') as file_stream:
                configs = yaml.load(file_stream)
                cls._mqs_config = configs.get(cls.run_mode)
        if cls._clients.get(name) is not None:
            return cls._clients[name]
        cls._clients[name] = MQClient(cls._mqs_config.get(name)['url'])
        return cls._clients[name]
