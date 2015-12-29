#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 2014-10-29
A lightweight wrapper around DatabaseFactory.
author: huwei
"""
import os
import yaml
from .database import DatabaseFactory

__author__ = 'freeway'


class DatabaseBuilder(object):

    _database_factories = None
    _databases_config = None
    run_mode = 'development'

    @classmethod
    def _get_db_instance_by_name(cls, name):
        if cls._database_factories is None or cls._database_factories[name] is None:
            if cls._database_factories is None:
                cls._database_factories = dict()
            if cls._databases_config is None:
                with file(os.path.join(os.getcwd(), 'databases.yaml'), 'r') as file_stream:
                    cls._databases_config = yaml.load(file_stream).get(cls.run_mode)
            database_config = cls._databases_config.get(name)
            if database_config is not None:
                cls._database_factories[name] = DatabaseFactory(**database_config)
        return cls._database_factories[name]

    @classmethod
    def get_default_db_instance(cls):
        return cls._get_db_instance_by_name('default')
