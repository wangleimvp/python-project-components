#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import deque
from threading import Condition
import logging
import pika
import thread
import tornado

__author__ = 'freeway'

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


class MqPublisher(object):
    """This is an example publisher that will handle unexpected interactions
    with RabbitMQ such as channel and connection closures.

    If RabbitMQ closes the connection, it will reopen it. You should
    look at the output, as there are limited reasons why the connection may
    be closed, which usually are tied to permission related issues or
    socket timeouts.

    It uses delivery confirmations and illustrates one way to keep track of
    messages that have been sent and if they've been confirmed by RabbitMQ.

    """

    def __init__(self, amqp_url,
                 exchange='',
                 exchange_type='fanout',
                 queue=None,
                 routing_key='',
                 durable=True,
                 properties=None):
        """Setup the example publisher object, passing in the URL we will use
        to connect to RabbitMQ.


        :param amqp_url: The URL for connecting to RabbitMQ
        :type amqp_url: str
        :param exchange:
        :type exchange:
        :param exchange_type:
        :type exchange_type:
        :param queue:
        :type queue:
        :param routing_key:
        :type routing_key:
        :param no_ack:
        :type no_ack:
        :param properties:
        :type properties:
        :return:
        :rtype:
        """
        self._deliveries = []
        self._acked = 0
        self._nacked = 0
        self._connection = None
        self._channel = None
        self._message_number = 0
        self._stopping = False
        self._url = amqp_url
        self._closing = False
        self._exchange = exchange
        self._exchange_type = exchange_type
        self._queue = queue
        self._routing_key = routing_key
        self._properties = properties
        self._durable = durable
        self._thread_conditiion = Condition()
        self._messages = deque([])

    def connect(self):
        """This method connects to RabbitMQ, returning the connection handle.
        When the connection is established, the on_connection_open method
        will be invoked by pika. If you want the reconnection to work, make
        sure you set stop_ioloop_on_close to False, which is not the default
        behavior of this adapter.

        :rtype: pika.SelectConnection

        """
        self._deliveries = []
        self._acked = 0
        self._nacked = 0
        self._message_number = 0

        LOGGER.info('Connecting to %s', self._url)
        self._connection = pika.SelectConnection(pika.URLParameters(self._url),
                                                  self.on_connection_open)
        return self._connection

    def close_connection(self):
        """This method closes the connection to RabbitMQ."""
        LOGGER.info('Closing connection')
        self._closing = True
        self._connection.close()

    def on_connection_open(self, unused_connection):
        """This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.

        :type unused_connection: pika.SelectConnection

        """
        LOGGER.info('Connection opened')
        self.add_on_connection_close_callback()
        self.open_channel()

    def add_on_connection_close_callback(self):
        LOGGER.info('Adding connection close callback')
        self._connection.add_on_close_callback(self.on_connection_closed)

    def on_connection_closed(self, connection, reply_code, reply_text):
        self._channel = None
        if not self._closing:
            LOGGER.warning('Connection closed, reopening in 5 seconds: (%s) %s',
                           reply_code, reply_text)
            self._connection.add_timeout(5, self.connect)

    def add_on_channel_close_callback(self):
        LOGGER.info('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reply_code, reply_text):
        """Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.

        :param pika.channel.Channel: The closed channel
        :param int reply_code: The numeric reason the channel was closed
        :param str reply_text: The text reason the channel was closed

        """
        LOGGER.warning('Channel was closed: (%s) %s', reply_code, reply_text)
        if not self._closing:
            self._connection.close()

    def on_channel_open(self, channel):
        """This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.

        Since the channel is now open, we'll declare the exchange to use.

        :param pika.channel.Channel channel: The channel object

        """
        LOGGER.info('Channel opened')
        self._channel = channel
        self.add_on_channel_close_callback()

        if 'fanout' == self._exchange_type:
            self.setup_exchange(self._exchange)
        else:
            self.setup_queue(self._queue)

    def setup_exchange(self, exchange_name):
        """Setup the exchange on RabbitMQ by invoking the Exchange.Declare RPC
        command. When it is complete, the on_exchange_declareok method will
        be invoked by pika.

        :param str|unicode exchange_name: The name of the exchange to declare

        """
        LOGGER.info('Declaring exchange %s', exchange_name)
        self._channel.exchange_declare(self.on_exchange_declareok,
                                       exchange_name,
                                       self._exchange_type)

    def on_exchange_declareok(self, unused_frame):
        """Invoked by pika when RabbitMQ has finished the Exchange.Declare RPC
        command.

        :param pika.Frame.Method unused_frame: Exchange.DeclareOk response frame

        """
        LOGGER.info('Exchange declared')
        self.start_publishing()

    def setup_queue(self, queue_name):
        """Setup the queue on RabbitMQ by invoking the Queue.Declare RPC
        command. When it is complete, the on_queue_declareok method will
        be invoked by pika.

        :param str|unicode queue_name: The name of the queue to declare.

        """
        LOGGER.info('Declaring queue %s', queue_name)
        self._channel.queue_declare(self.on_queue_declareok, queue=queue_name, durable=self._durable)

    def on_queue_declareok(self, method_frame):
        """Method invoked by pika when the Queue.Declare RPC call made in
        setup_queue has completed. In this method we will bind the queue
        and exchange together with the routing key by issuing the Queue.Bind
        RPC command. When this command is complete, the on_bindok method will
        be invoked by pika.

        :param pika.frame.Method method_frame: The Queue.DeclareOk frame

        """
        # LOGGER.info('binding %s to %s with %s',
        #             self._exchange, self._queue, self._routing_key)
        # self._channel.queue_bind(self.on_bindok, self._queue,
        #                          self._exchange, self._routing_key)
        self.start_publishing()

    def publish_message(self, message):
        """If the class is not stopping, publish a message to RabbitMQ,
        appending a list of deliveries with the message number that was sent.
        This list will be used to check for delivery confirmations in the
        on_delivery_confirmations method.

        Once the message has been sent, schedule another message to be sent.
        The main reason I put scheduling in was just so you can get a good idea
        of how the process is flowing by slowing down and speeding up the
        delivery intervals by changing the PUBLISH_INTERVAL constant in the
        class.

        """
        if self._stopping:
            return

        self._thread_conditiion.acquire()
        self._messages.append(message)
        self._thread_conditiion.notify_all()
        self._thread_conditiion.release()

    def start_publishing(self):
        """This method will enable delivery confirmations and schedule the
        first message to be sent to RabbitMQ

        """
        self.enable_delivery_confirmations()
        self.process_messages()


    def enable_delivery_confirmations(self):
        """Send the Confirm.Select RPC method to RabbitMQ to enable delivery
        confirmations on the channel. The only way to turn this off is to close
        the channel and create a new one.

        When the message is confirmed from RabbitMQ, the
        on_delivery_confirmation method will be invoked passing in a Basic.Ack
        or Basic.Nack method from RabbitMQ that will indicate which messages it
        is confirming or rejecting.

        """
        self._channel.confirm_delivery(self.on_delivery_confirmation)

    def on_delivery_confirmation(self, method_frame):
        """Invoked by pika when RabbitMQ responds to a Basic.Publish RPC
        command, passing in either a Basic.Ack or Basic.Nack frame with
        the delivery tag of the message that was published. The delivery tag
        is an integer counter indicating the message number that was sent
        on the channel via Basic.Publish. Here we're just doing house keeping
        to keep track of stats and remove message numbers that we expect
        a delivery confirmation of from the list used to keep track of messages
        that are pending confirmation.

        :param pika.frame.Method method_frame: Basic.Ack or Basic.Nack frame

        """
        confirmation_type = method_frame.method.NAME.split('.')[1].lower()
        LOGGER.info('Received %s for delivery tag: %i',
                    confirmation_type,
                    method_frame.method.delivery_tag)
        if confirmation_type == 'ack':
            self._acked += 1
        elif confirmation_type == 'nack':
            self._nacked += 1
        self._deliveries.remove(method_frame.method.delivery_tag)
        LOGGER.info('Published %i messages, %i have yet to be confirmed, '
                    '%i were acked and %i were nacked',
                    self._message_number, len(self._deliveries),
                    self._acked, self._nacked)

    def process_messages(self):
        while True:
            self._thread_conditiion.acquire()
            if len(self._messages) == 0:
                self._thread_conditiion.wait()
            else:
                if not self._channel:
                    self._thread_conditiion.wait(timeout=2)
                    continue
                message = self._messages.popleft()
                if 'fanout' == self._exchange_type:
                    self._channel.basic_publish(self._exchange, self._routing_key, message, properties=self._properties)
                else:
                    self._channel.basic_publish(self._exchange, self._queue, message, properties=self._properties)
                self._message_number += 1
                self._deliveries.append(self._message_number)
                LOGGER.info('Published message # %i: %s', self._message_number, message)
            self._thread_conditiion.release()

    def on_bindok(self, unused_frame):
        """This method is invoked by pika when it receives the Queue.BindOk
        response from RabbitMQ. Since we know we're now setup and bound, it's
        time to start publishing."""
        LOGGER.info('Queue bound')
        self.start_publishing()

    def close_channel(self):
        """Invoke this command to close the channel with RabbitMQ by sending
        the Channel.Close RPC command.

        """
        LOGGER.info('Closing the channel')
        if self._channel:
            self._channel.close()

    def open_channel(self):
        """This method will open a new channel with RabbitMQ by issuing the
        Channel.Open RPC command. When RabbitMQ confirms the channel is open
        by sending the Channel.OpenOK RPC reply, the on_channel_open method
        will be invoked.

        """
        LOGGER.info('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def run(self):
        self.connect()
        thread.start_new_thread(self._connection.ioloop.start, ())

    def stop(self):
        """Stop the example by closing the channel and connection. We
        set a flag here so that we stop scheduling new messages to be
        published. The IOLoop is started because this method is
        invoked by the Try/Catch below when KeyboardInterrupt is caught.
        Starting the IOLoop again will allow the publisher to cleanly
        disconnect from RabbitMQ.

        """
        LOGGER.info('Stopping')
        self._stopping = True
        self.close_channel()
        self.close_connection()
        self._connection.ioloop.start()
        LOGGER.info('Stopped')


def main():
    logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

    # Connect to localhost:5672 as guest with the password guest and virtual host "/" (%2F)
    example = MqPublisher('amqp://192.168.0.201:5672/%2F?connection_attempts=99999999999&heartbeat_interval=5',
                          exchange='web_socket',
                          exchange_type='fanout',
                          queue=None,
                          routing_key='')

    example2 = MqPublisher('amqp://192.168.0.201:5672/%2F?connection_attempts=99999999999&heartbeat_interval=5',
                           exchange='',
                           exchange_type='',
                           queue='test',
                           routing_key='test',
                           durable=True,
                           properties=pika.BasicProperties(delivery_mode=2))

    try:
        import thread
        from time import sleep
        from app.commons import jsonutil
        example.run()
        i = 0
        while True:
            i += 1
            msg = dict()
            msg[u"user_id"] = u'd1116eb1-0f77-4edc-8c4f-a421b9e41618'
            msg["data"] = {"badges":{"participant": 1+i, "post": 32+i, "comment": i*2, "party_changed": i*3}}
            sleep(1)
            example.publish_message(jsonutil.json_encode(msg))
            msg[u"user_id"] = 'LE8'
            example.publish_message(jsonutil.json_encode(msg))
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
        example2.stop()


if __name__ == '__main__':
    main()
