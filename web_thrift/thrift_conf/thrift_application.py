#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# thrift 服务注册 启动
#
import logging
import sys

import tornado
from thrift.TMultiplexedProcessor import TMultiplexedProcessor
from tornado.options import define

from web_thrift.gen_py.test import ThriftTestService
from web_thrift.thrift_conf.thrift_builder import ThriftBuilder
from web_thrift.thrift_server.party_thrift_handler import ThriftTestHandler

reload(sys)
sys.setdefaultencoding('utf8')
define("runmod", default='development', help="runing mod. [development|test|production]")
define("app_name", default='None')

tornado.options.parse_command_line()


def sig_handler(sig, frame):
    logging.warning('Caught signal: %s', sig)
    shutdown()


def shutdown():
    exit(0)


def main():
    multiplexed_processor = TMultiplexedProcessor()

    processor = ThriftTestService.Processor(ThriftTestHandler())
    multiplexed_processor.registerProcessor("test_service", processor)

    ThriftBuilder.start_server_by_name(multiplexed_processor, name='default')

if __name__ == "__main__":
    main()
