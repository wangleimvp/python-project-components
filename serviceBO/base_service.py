#!/usr/bin/env python
# -*- coding: utf-8 -*-
from contextlib import contextmanager
import logging
from atomiclong import AtomicLong
from serviceBO.biz_model import BizModel, Attribute

__author__ = 'freeway'


class ContextBO(BizModel):
    current_user_id = Attribute(None)
    remote_ip = Attribute(None)
    runmod = Attribute(None)


class ReqBO(BizModel):
    context = Attribute(None, attri_type=ContextBO)


class ServiceError(Exception):

    RESPONSE_ERROR = 1002
    """服务错误
    一些无法解决的一些错误被称为系统错误，
    比如数据库访问失败，数据库插入失败等."""

    def __init__(self, code, msg, *args, **kwargs):
        """初始化

        :param code: 错误码
        :param msg:
        :param args:
        :param kwargs:
        """
        self.code = code
        self.msg = msg
        super(ServiceError, self).__init__(*args, **kwargs)


class ServiceException(Exception):
    """服务异常
    主要针对于一些逻辑异常，就抛出相关的错误。
    比如当前用户不存在，名称不能为空
    """

    def __init__(self, code, msg, *args, **kwargs):
        """初始化

        :param code: 错误码
        :param args:
        :param kwargs:
        """
        self.code = code
        self.msg = msg
        super(ServiceException, self).__init__(*args, **kwargs)


class ServiceValidationFailsException(Exception):

    def __init__(self, msg, *args, **kwargs):
        """初始化

        :param code: 错误码
        :param args:
        :param kwargs:
        """
        self.code = 10000
        self.msg = msg
        super(ServiceValidationFailsException, self).__init__(*args, **kwargs)


class BaseService(object):
    session_count = dict()
    @contextmanager
    def create_session(self, db):
        """Provide a transactional scope around a series of operations.
        :param db: DatabaseFactory database factory
        """
        session = db.session_cls()
        session_id = id(session)
        try:
            s = self.session_count.get(session_id, None)
            if s is None:
                self.session_count[session_id] = AtomicLong(1)
            else:
                self.session_count[session_id] += 1
            yield session
            self.session_count[session_id] -= 1
            session.commit()
        except Exception as e:
            if isinstance(e, (ServiceException, ServiceValidationFailsException)):
                session.commit()
                raise e
            else:
                session.rollback()
                logging.exception(e)
                raise e
                # raise ServiceError(10001, 'Service error')
        finally:
            if self.session_count[session_id].value == 0:
                session.close()