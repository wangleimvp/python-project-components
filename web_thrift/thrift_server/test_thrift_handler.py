#!/usr/bin/env python
# -*- coding: utf-8 -*-
import functools
import logging
import sys

from web_thrift.gen_py.test.ttypes import ThriftException

reload(sys)
sys.setdefaultencoding('utf8')


def thrift_exception(method):
    @functools.wraps(method)
    def _wapper(*args, **kwargs):
        try:
            return method(*args, **kwargs)
        except Exception:
            raise ThriftException(1000, 'system error')
    return _wapper


class ThriftTestHandler(object):
    """

    """
    @staticmethod
    def test_thrift(thrift_strings):
        """

        :param thrift_strings:
        :return:
        """
        return 'thrift success: ' + thrift_strings
