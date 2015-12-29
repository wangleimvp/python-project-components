#!/usr/bin/env python
# -*- coding: utf-8 -*-
from web_thrift.gen_py.test import ThriftTestService
from web_thrift.thrift_conf.thrift_builder import ThriftBuilder

__author__ = 'wangshubin'


if __name__ == "__main__":

    client = ThriftBuilder.get_client("test_service", ThriftTestService)
    print client.test_thrift('hello word!')
