#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import random
import pygeoip
from app.commons.base_service import BaseService
from app.commons.memcache_factory import MemCacheFactory
from configs.settings import Settings


__author__ = 'freeway'


class GeohashCacheService(BaseService):

    _cache_session = 'geohash'

    @classmethod
    def _parse_to_key(cls, current_time, geo_hashcode):
        return "parties:{0}_{1}".format(current_time, geo_hashcode[:-1])

    @classmethod
    def set_to_memcached(cls, current_time, geo_hashcode, data_source):
        """ 把数据加入缓存

        :param geo_hashcode:
        :param data_source:  加入缓存的数据
        :return:
        """
        cache_factory = MemCacheFactory.get_instance(cls._cache_session)
        key = cls._parse_to_key(current_time, geo_hashcode)
        cache_factory.set(key, data_source)

    @classmethod
    def get_by_memcached(cls, current_time, geo_hashcode):
        """ 从缓存中获取数据

        :param geo_hashcode:
        :return:
        """
        cache_factory = MemCacheFactory.get_instance(cls._cache_session)
        key = cls._parse_to_key(current_time, geo_hashcode)
        cached_date = cache_factory.get(key)
        if cached_date is None:
            return []
        return cached_date

    @classmethod
    def delete_by_memcached(cls, current_time, geo_hashcode):
        """ 从缓存中获取数据

        :param geo_hashcode:
        :return:
        """
        cache_factory = MemCacheFactory.get_instance(cls._cache_session)
        key = cls._parse_to_key(current_time, geo_hashcode)
        cached_date = cache_factory.get(key)
        if cached_date is not None:
            cache_factory.delete(key)


class GeoIpService(BaseService):

    geo_ip = None

    @classmethod
    def get_geo_ip(cls):
        if cls.geo_ip is None:
            city_file = os.path.join(Settings.SITE_ROOT_PATH, u"app/services/GeoLiteCity.dat")
            cls.geo_ip = pygeoip.GeoIP(city_file)
        return cls.geo_ip