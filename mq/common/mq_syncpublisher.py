#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
from collections import deque
from threading import Condition
import logging
import pika
import tornado

__author__ = 'freeway'

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


class MQPublisherProducter(object):

    def __init__(self, condition, messages):
        """

        :param condition:
        :type condition:
        :param messages:
        :type messages: collections.deque
        :return:
        :rtype:
        """
        self._thread_condition = condition
        self._messages = messages

    def send(self, queue_name, message, durable=True):
        self._thread_condition.acquire()
        self._messages.append((MQPublisher.MQ_TYPE_DIRECT, queue_name, message, durable))
        self._thread_condition.notify()
        self._thread_condition.release()

    def send_all(self, queue_name, messages, durable=True):
        self._thread_condition.acquire()
        for message in messages:
            self._messages.append((MQPublisher.MQ_TYPE_DIRECT, queue_name, message, durable))
        self._thread_condition.notify()
        self._thread_condition.release()

    def publish(self, queue_name, message):
        self._thread_condition.acquire()
        self._messages.append((MQPublisher.MQ_TYPE_FANOUT, queue_name, message))
        self._thread_condition.notify()
        self._thread_condition.release()

    def publish_all(self, queue_name, messages):
        self._thread_condition.acquire()
        for message in messages:
            self._messages.append((MQPublisher.MQ_TYPE_FANOUT, queue_name, message))
        self._thread_condition.notify()
        self._thread_condition.release()


class MQPublisherConsumer(threading.Thread):

    def __init__(self, url, messages):
        """

        :param url:
        :type url:
        :param messages:
        :type messages: collections.deque
        :return:
        :rtype:
        """

        super(MQPublisherConsumer, self).__init__()
        self.url = url
        self._thread_condition = Condition()
        self._messages = messages
        self._send_connection = None
        self._send_channels = None
        self._is_closed = False

    def get_condition(self):
        return self._thread_condition

    def stop(self):
        self._is_closed = True
        self._thread_condition.acquire()
        self._thread_condition.notify()
        self._thread_condition.release()

    def _get_channel(self, queue_type, queue_name, *args):

        if self._send_connection is None or (not self._send_connection.is_open):
            self._send_connection = pika.BlockingConnection(pika.URLParameters(self.url))
            self._send_channels = dict()

        channel_key = "{0}_{1}".format(queue_type, queue_name)
        channel = self._send_channels.get(channel_key, None)

        if channel is None:
            channel = self._send_connection.channel()
            if "direct" == queue_type:
                channel.queue_declare(queue=queue_name, durable=args[0])
                self._send_channels[channel_key] = channel
            else:
                channel.exchange_declare(exchange=queue_name,
                                         type='fanout')
                self._send_channels[channel_key] = channel

        return channel

    def run(self):
        while True and (not self._is_closed):
            self._thread_condition.acquire()
            if len(self._messages) == 0:
                logging.info('no message waiting...')
                self._thread_condition.wait()
            else:
                message = self._messages.popleft()
                queue_type = message[0]
                body = message[2]
                if body is None:
                    continue
                if "direct" == queue_type:

                    queue = message[1]
                    durable = message[3]
                    try:
                        channel = self._get_channel(queue_type, queue, durable)
                        properties = pika.BasicProperties(delivery_mode=2) if durable else None
                        channel.basic_publish(exchange='',
                                              routing_key=queue,
                                              body=body,
                                              properties=properties)
                    except Exception as e:
                        self._messages.appendleft(message)
                        logging.exception(e)
                        self._send_connection = None
                else:
                    queue = message[1]
                    body = message[2]
                    try:
                        channel = self._get_channel(queue_type, queue)
                        channel.basic_publish(exchange=queue, routing_key='', body=body)
                    except Exception as e:
                        logging.exception(e)
                        self._messages.appendleft(message)
                        self._send_connection = None

            self._thread_condition.release()


class MQPublisher(object):

    MQ_TYPE_DIRECT = "direct"
    MQ_TYPE_FANOUT = "fanout"

    def __init__(self, url):
        self._messages = deque([])
        self._url = url
        consumer = MQPublisherConsumer(self._url, self._messages)
        condition = consumer.get_condition()
        self.producter = MQPublisherProducter(condition, self._messages)
        consumer.start()
        self._consumer = consumer

    def send(self, queue_name, message, durable=True):
        self.producter.send(queue_name, message, durable)

    def send_all(self, queue_name, messages, durable=True):
        self.producter.send_all(queue_name, messages, durable)

    def publish(self, queue_name, message):
        self.producter.publish(queue_name, message)

    def publish_all(self, queue_name, messages):
        self.producter.publish_all(queue_name, messages)

    def stop(self):
        self._consumer.stop()

def main():
    logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

    # Connect to localhost:5672 as guest with the password guest and virtual host "/" (%2F)
    example = MQPublisher('amqp://192.168.0.201:5672/%2F?connection_attempts=99999999999&heartbeat_interval=5')

    try:
        import thread
        from time import sleep
        from app.commons import jsonutil
        i = 0
        while True:
            i += 1
            msg = dict()
            msg[u"user_id"] = u'd1116eb1-0f77-4edc-8c4f-a421b9e41618'
            msg["data"] = {"badges":{"participant": 1+i, "post": 32+i, "comment": i*2, "party_changed": i*3}}
            sleep(1)
            example.publish('web_socket', jsonutil.json_encode(msg))
            msg[u"user_id"] = 'LE8'
            example.publish('web_socket', jsonutil.json_encode(msg))
            example.send('test', jsonutil.json_encode(msg), durable=True)
        #
        # example.publish_message("hehehe,hsdhasd")
        # example.publish_message("hehehe,12313")
        # example.publish_message("hehehe,3443")
        # example.publish_message("hehehe,werwer")
        # example.publish_message("hehehe,erwer")
        # example.publish_message("hehehe,rtrtrt")

        # example2.run()
        # while True:
        #     example2.publish_message("test.hahhas")
        #
        #     example2.publish_message("test2.hahhas")
        #     example2.publish_message("test3.4234")
        #     example2.publish_message("tes4t.hahhas")
        #     example2.publish_message("tes5t.hahhas")
        #     example2.publish_message("test5.324")
        #     sleep(3)

        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
