#!/usr/bin/env python
# -*- coding: utf-8 -*-
from mq.common.mq_consumer import MQConsumer
from mq_syncpublisher import MQPublisher

__author__ = 'freeway'


class MQClient(object):

    def __init__(self, url, *args, **kwargs):
        """ 初始化

        :param url:
        :type url:
        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """
        self.url = url
        self._receive_consumers = dict()
        self._sub_consumers = dict()
        self._publisher = MQPublisher(url)

    def send(self, queue_name, message, durable=True):
        self._publisher.send(queue_name, message, durable=durable)

    def send_all(self, queue_name, messages, durable=True):
        self._publisher.send_all(queue_name, messages, durable=durable)

    def publish(self, queue_name, message):
        self._publisher.publish(queue_name, message)

    def publish_all(self, queue_name, messages):
        self._publisher.publish_all(queue_name, messages)

    def receive(self, queue_name, callback, no_ack=False):
        """ 接收

        :param queue_name:
        :type queue_name: str
        :param callback:
        :type callback: func
        :param no_ack:
        :type no_ack: bool
        :return:
        :rtype:
        """
        consumer = self._receive_consumers.get(queue_name, None)
        if consumer is None:
            consumer = MQConsumer(self.url,
                                  exchange='',
                                  no_ack=no_ack,
                                  exchange_type='',
                                  queue=queue_name,
                                  routing_key='',
                                  callback=callback)
            consumer.run()
            self._receive_consumers[queue_name] = consumer

    def subscribe(self, queue_name, callback):
        """ 订阅

        :param queue_name:
        :type queue_name: str
        :param callback:
        :type callback: func
        :return:
        :rtype: None
        """
        consumer = self._sub_consumers.get(queue_name, None)
        if consumer is None:
            consumer = MQConsumer(self.url,
                                  exchange=queue_name,
                                  exchange_type='fanout',
                                  queue=None,
                                  routing_key='',
                                  callback=callback)
            consumer.run()
            self._sub_consumers[queue_name] = consumer

    def stop(self):

        self._publisher.stop()
        for k, v in self._receive_consumers.iteritems():
            v.stop()

        for k, v in self._sub_consumers.iteritems():
            v.stop()