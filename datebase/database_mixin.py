#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import Column, BigInteger, Boolean, String

__author__ = 'freeway'


class IdMixin(object):
    id = Column(BigInteger, primary_key=True)


class IdStringMixin(object):
    id = Column(String(), primary_key=True)


class CreatedAtMixin(object):
    created_at = Column(BigInteger)


class UpdatedAtMixin(object):
    updated_at = Column(BigInteger)


class IsDeletedMixin(object):
    is_deleted = Column(Boolean, default=False)
