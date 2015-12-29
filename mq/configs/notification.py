#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import signal
import sys

import tornado
import yaml
from tornado.ioloop import IOLoop
from tornado.options import options, define

reload(sys)
sys.setdefaultencoding('utf8')
define("runmod", default='development', help="runing mod. [development|test|production]")
define("app_name", default='None')
tornado.options.parse_command_line()

#set run mode
from upload.upload_factory import UploadFactory
UploadFactory.run_mode = options.runmod

from mq.configs.mq_builder import MQBuilder
MQBuilder.run_mode = options.runmod

from web_thrift.thrift_builder.thrift_builder import ThriftBuilder
ThriftBuilder.run_mode = options.runmod

from memcache.memcache_factory import MemCacheFactory
MemCacheFactory.run_mode = options.runmod

from wechat.wechat_builder import WeChatBuilder
WeChatBuilder.run_mode = options.runmod

from datebase.database_builder import DatabaseBuilder
DatabaseBuilder.run_mode = options.runmod

from wechat.weixin_template_builder import WeixinTemplateBuilder
WeixinTemplateBuilder.run_mode = options.runmod


from mq.service.mq_receive_service import MQReceiveService
from mq.service.mq_send_service import QueueName
from configs.settings import Settings

__author__ = 'freeway'


def sig_handler(sig, frame):
    logging.warning('Caught signal: %s', sig)
    shutdown()


def shutdown():
    mq_client.stop()
    IOLoop.instance().stop()
    exit(0)


def main():

    file_stream = file(os.path.join(Settings.SITE_ROOT_PATH, 'configs', 'settings.yaml'), 'r')
    yml = yaml.load(file_stream)
    yml_settings = yml.get(options.runmod)
    Settings.WEBSITE = yml_settings['website']
    Settings.SITE_NAME = yml_settings['sitename']
    Settings.SITE_ROOT = u'http://' + Settings.WEBSITE

    global mq_client
    mq_client = MQBuilder.get_mq_client_by_name('default')
    mq_client.receive(QueueName.JOIN_PARTY, MQReceiveService.add_party_callback)
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    IOLoop.instance().start()

if __name__ == "__main__":
    main()
