#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import datetime
from tornado.ioloop import IOLoop

from tornado.web import RequestHandler

from tornado.websocket import WebSocketHandler

from commons import jsonutil
from service_bo.user_service import UserService

__author__ = 'freeway'


class SocketHandler(WebSocketHandler):
    _socket_handlers = dict()
    _heart_beat = 30
    _heart_beat_time_out = 5

    @staticmethod
    def on_sub_message(message):
        """

        :param queue:
        :type queue: str
        :return:
        :rtype: str
        """
        if message is None:
            return
        msg = jsonutil.json_decode(message)
        user_id = msg.get("user_id", None)
        if user_id is None or len(user_id) == 0:
            return
        data = msg.get("data", None)
        if data is None:
            return
        users = SocketHandler._socket_handlers.get(user_id, None)
        if users is None:
            return
        need_deleted_keys = []
        for key, handler in users.iteritems():
            try:
                handler.write_message(data)
            except Exception as e:
                handler.close()
                need_deleted_keys.append(key)

        for key in need_deleted_keys:
            del users[key]

    def __init__(self, application, request, **kwargs):
        WebSocketHandler.__init__(self, application, request, **kwargs)
        self.io_loop = IOLoop.instance()
        self.heart_beat = None
        self.ping_timeout = None

    def open(self):
        """ 创建长连接

        :return:
        :rtype:
        """
        if not self.current_user:
            self.close(code=403, reason="必须是登录用户才可以访问")
            return
        users = self.__class__._socket_handlers.get(self.current_user.user_id, None)
        if users is None:
            users = dict()
            self.__class__._socket_handlers[self.current_user.user_id] = users
        users[id(self)] = self

        # Ping to make sure the agent is alive.
        self.heart_beat = self.io_loop.add_timeout(datetime.timedelta(seconds=self._heart_beat), self.send_ping)

    def on_connection_timeout(self):
        self.close()

    def send_ping(self):
        logging.debug("<- [PING]")
        try:
            self.ping(str(id(self)))
            self.ping_timeout = self.io_loop.add_timeout(datetime.timedelta(seconds=self._heart_beat_time_out),
                                                         self.on_connection_timeout)
        except Exception as e:
            self.on_close()

    def on_pong(self, data):
        logging.debug("-> [PONG] %s" % data)

        if self.ping_timeout:
            self.io_loop.remove_timeout(self.ping_timeout)
            self.ping_timeout = None

        self.heart_beat = self.io_loop.add_timeout(datetime.timedelta(seconds=self._heart_beat), self.send_ping)

    def on_close(self):
        """ 释放长连接

        :return:
        :rtype:
        """
        if self.current_user:
            users = self.__class__._socket_handlers.get(self.current_user.user_id, None)
            if users is not None:
                del users[id(self)]

        if self.ping_timeout:
            self.io_loop.remove_timeout(self.ping_timeout)
            self.ping_timeout = None

        if self.heart_beat:
            self.io_loop.remove_timeout(self.heart_beat)
            self.heart_beat = None

    def set_default_headers(self):
        """Override this to set HTTP headers at the beginning of the request.

        For example, this is the place to set a custom ``Server`` header.
        Note that setting such headers in the normal flow of request
        processing may not do what you want, since headers may be reset
        during error handling.
        """
        self.clear_header("Server")

    def get_current_user(self):
        """

        :return:
        :rtype: app.services.bos.user.UserRespBO
        """
        user_id = self.get_secure_cookie("ut_user_id")
        if not user_id:
            return None
        else:
            user = UserService().get_user(user_id)
            return user if user else None


class SocketIndexHandler(RequestHandler):
    def get(self):
        self.write('''
<html>
<head>
<script>
var ws = new WebSocket('ws://www.j.com:8084/soc');
ws.onmessage = function(event) {
    document.getElementById('message').innerHTML = event.data;
    console.log(event.data)
};
</script>
</head>
<body>
<p id='message'></p>
        ''')
