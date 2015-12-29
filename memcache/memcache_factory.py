#!/usr/bin/env python
# -*- coding: utf-8 -*-
from _pylibmc import ConnectionError, MemcachedError
import functools
import logging
import os
import yaml

__author__ = 'freeway'

from pylibmc.client import Client


class MemCacheFactory(object):
    """
    memory cache factory
    """

    memcache_configs = None
    memcache_dict = dict()
    run_mode = 'development'

    @classmethod
    def get_instance(cls, session, run_mode=None):
        if not cls.memcache_configs:
            with file(os.path.join(os.getcwd(), 'memcaches.yaml'), 'r') as file_stream:
                yml = yaml.load(file_stream)
            if run_mode is None:
                run_mode = cls.run_mode
            cls.memcache_configs = yml.get(run_mode)

        memcache_factory = cls.memcache_dict.get(session, None)
        if memcache_factory is not None:
            return memcache_factory

        memcache_config = cls.memcache_configs.get(session)
        if not memcache_config.get("enabled", False):
            return None
        if memcache_config is not None:
            memcache_factory = MemCacheFactory(memcache_config.get('servers'),
                                               behaviors=memcache_config.get('behaviors'),
                                               binary=memcache_config.get('binary'),
                                               username=memcache_config.get('username'),
                                               password=memcache_config.get('password'))
            cls.memcache_dict[session] = memcache_factory
            return memcache_factory
        else:
            return None

    def __init__(self, servers, behaviors=None, binary=False, username=None, password=None):
            self._client = Client(servers, behaviors, binary, username, password)

    def add(self, *args, **kwargs):
        try:
            """ Set a key only if doesn't exist. """
            return self._client.add(*args, **kwargs)
        except MemcachedError as e:
            logging.exception(e)
            return None

    def add_multi(self, *args, **kwargs):
        try:
            """ Add multiple keys at once. """
            return self._client.add_multi(*args, **kwargs)
        except ConnectionError as e:
            logging.exception(e)
            return None

    def append(self, *args, **kwargs):
        try:
            """ Append data to a key. """
            return self._client.append(*args, **kwargs)
        except MemcachedError as e:
            logging.exception(e)
            return None

    def cas(self, *args, **kwargs):
        try:
            """ Attempt to compare-and-store a key by CAS ID. """
            return self._client.cas(*args, **kwargs)
        except ConnectionError as e:
            logging.exception(e)
            return None

    def decr(self, *args, **kwargs):
        try:
            """ Decrement a key by a delta. """
            return self._client.decr(*args, **kwargs)
        except MemcachedError as e:
            logging.exception(e)
            return None

    def delete(self, *args, **kwargs):
        try:
            """ Delete a key. """
            return self._client.delete(*args, **kwargs)
        except MemcachedError as e:
            logging.exception(e)
            return None

    def delete_multi(self, *args, **kwargs):
        try:
            """ Delete multiple keys at once. """
            return self._client.delete_multi(*args, **kwargs)
        except MemcachedError as e:
            logging.exception(e)
            return None

    def disconnect_all(self, *args, **kwargs):
        try:
            """ Disconnect from all servers and reset own state. """
            return self._client.disconnect_all(*args, **kwargs)
        except ConnectionError as e:
            logging.exception(e)
            return None

    def flush_all(self, *args, **kwargs):
        try:
            """ Flush all data on all servers. """
            return self._client.flush_all(*args, **kwargs)
        except MemcachedError as e:
            logging.exception(e)
            return None


    def get(self, *args, **kwargs):
        try:
            """ Retrieve a key from a memcached. """
            return self._client.get(*args, **kwargs)
        except ConnectionError as e:
            logging.exception(e)
            return None


    def gets(self, *args, **kwargs):
        try:
            """ Retrieve a key and cas_id from a memcached. """
            return self._client.gets(*args, **kwargs)
        except MemcachedError as e:
            logging.exception(e)
            return None

    def get_behaviors(self, *args, **kwargs):
        try:
            """ Get behaviors dict. """
            return self._client.get_behaviors(*args, **kwargs)
        except MemcachedError as e:
            logging.exception(e)
            return None

    def get_multi(self, *args, **kwargs):
        try:
            """ Get multiple keys at once. """
            return self._client.get_multi(*args, **kwargs)
        except MemcachedError as e:
            logging.exception(e)
            return None

    def get_stats(self, *args, **kwargs):
        try:
            """ Retrieve statistics from all memcached servers. """
            return self._client.get_stats(*args, **kwargs)
        except MemcachedError as e:
            logging.exception(e)
            return None

    def hash(self, *args, **kwargs):
        try:
            """ Hash value of *key*. """
            return self._client.hash(*args, **kwargs)
        except MemcachedError as e:
            logging.exception(e)
            return None

    def incr(self, *args, **kwargs):
        try:
            """ Increment a key by a delta. """
            return self._client.incr(*args, **kwargs)
        except MemcachedError as e:
            logging.exception(e)
            return None

    def incr_multi(self, *args, **kwargs):
        try:
            """ Increment more than one key by a delta. """
            return self._client.incr_multi(*args, **kwargs)
        except ConnectionError as e:
            logging.exception(e)
            return None

    def prepend(self, *args, **kwargs):
        try:
            """ Prepend data to  a key. """
            return self._client.prepend(*args, **kwargs)
        except MemcachedError as e:
            logging.exception(e)
            return None

    def replace(self, *args, **kwargs):
        """ Set a key only if it exists. """
        try:
            return self._client.replace(*args, **kwargs)
        except MemcachedError as e:
            logging.exception(e)
            return None

    def set(self, *args, **kwargs):
        """ Set a key unconditionally. """
        try:
            return self._client.set(*args, **kwargs)
        except MemcachedError as e:
            logging.exception(e)
            return None

    def set_behaviors(self, *args, **kwargs):
        """ Set behaviors dict. """
        try:
            return self._client.set_behaviors(*args, **kwargs)
        except MemcachedError as e:
            logging.exception(e)
            return None

    def set_multi(self, *args, **kwargs):
        """ Set multiple keys at once. """
        try:
            return self._client.set_multi(*args, **kwargs)
        except ConnectionError as e:
            logging.exception(e)
            return None

    def touch(self, *args, **kwargs):
        """ Change the TTL of a key. """
        try:
            return self._client.touch(*args, **kwargs)
        except ConnectionError as e:
            logging.exception(e)
            return None


def cache_get(session=None, name=None):
    """
    get cache data
    :param session: cache session name
    :param name: cache name
    :return:
    """
    def _wrapper(func):
        @functools.wraps(func)
        def __wrapper(self, *args, **kwargs):
            factory = MemCacheFactory.get_instance(session)
            if factory is None:
                return func(self, *args, **kwargs)
            if len(args) == 1:
                factory = MemCacheFactory.get_instance(session)
                cache_key = "{0}:{1}".format(name, str(args[0]))
                cache_obj = factory.get(cache_key)
                if cache_obj is None:
                    obj = func(self, *args, **kwargs)
                    factory.set(cache_key, "None") if obj is None else factory.set(cache_key, obj)
                    return obj
                elif cache_obj == "None":
                    return None
                else:
                    return cache_obj
            else:
                return func(self, *args, **kwargs)
        return __wrapper
    return _wrapper


def cache_get_multi(session=None, name=None):
    """
    get multi cache data
    :param session: cache session name
    :param name: cache name
    :return:
    """
    def _wrapper(func):
        @functools.wraps(func)
        def __wrapper(self, *args, **kwargs):
            factory = MemCacheFactory.get_instance(session)
            if factory is None:
                return func(self, *args, **kwargs)
            if len(args) == 1 and isinstance(args[0], list):
                keys = args[0]
                if keys is None or len(keys) == 0:
                    return []

                str_keys = [str(key) for key in keys]
                cache_keys = ["%s:%s".format(name, key) for key in str_keys]
                cache_obj_dict = factory.get_multi(cache_keys)
                if len(cache_obj_dict) == 0:
                    results = func(self, *args, **kwargs)
                    if len(results) > 0:
                        if hasattr(results[0], 'id'):
                            factory.set_multi({"%s:%s".format(name, obj.id): obj for obj in results})
                    return results

                else:
                    if len(cache_keys) > len(cache_obj_dict):
                        # some data no cached, from db get data, and merge it.
                        cached_keys = [cache_key.split(":", 1)[1] for cache_key in cache_obj_dict.keys()]

                        no_cached_ids = \
                            [long(no_cache_key) for no_cache_key in list(set(str_keys).difference(set(cached_keys)))]
                        results = func(self, *[no_cached_ids], **kwargs)
                        if len(results) > 0:
                            if hasattr(results[0], 'id'):
                                need_set_dict = {"{0}:{1}".format(name, str(obj.id)): obj for obj in results}
                                factory.set_multi(need_set_dict)
                                cache_obj_dict.update(need_set_dict)

                    results = []
                    for cache_key in cache_keys:
                        result = cache_obj_dict.get(cache_key, None)
                        if result is not None:
                            results.append(result)
                    return results
            else:
                return func(self, *args, **kwargs)
        return __wrapper
    return _wrapper

def cache_set(session=None, name=None, key_attr=None):
    def _wrapper(func):
        @functools.wraps(func)
        def __wrapper(self, *args, **kwargs):
            factory = MemCacheFactory.get_instance(session)
            if factory is None:
                return func(self, *args, **kwargs)
            if len(args) == 1:
                if hasattr(args[0], key_attr):
                    cache_key = "{0}:{1}".format(name, str(getattr(args[0], key_attr)))
                    obj = func(self, *args, **kwargs)
                    factory.set(cache_key, "None") if args[0] is None else factory.set(cache_key, args[0])
                    return obj
            return func(self, *args, **kwargs)

        return __wrapper
    return _wrapper


def cache_delete(session=None, name=None):
    """
    delete cache data
    :param session: cache session name
    :param name: cache name
    :return:
    """
    def _wrapper(func):
        @functools.wraps(func)
        def __wrapper(self, *args, **kwargs):
            factory = MemCacheFactory.get_instance(session)
            if factory is None:
                return func(self, *args, **kwargs)
            if len(args) == 1:
                cache_key = "{0}:{1}".format(name, str(args[0]))
                factory.delete(cache_key)
                return func(self, *args, **kwargs)
            else:
                return func(self, *args, **kwargs)
        return __wrapper
    return _wrapper


def cache_delete_multi(session=None, name=None):
    """
    delete cache data
    :param session: cache session name
    :param name: cache name
    :return:
    """
    def _wrapper(func):
        @functools.wraps(func)
        def __wrapper(self, *args, **kwargs):
            factory = MemCacheFactory.get_instance(session)
            if factory is None:
                return func(self, *args, **kwargs)
            if len(args) == 1 and isinstance(args[0], list):
                keys = args[0]
                if keys is None or len(keys) == 0:
                    return 0
                factory.delete_multi(["{0}:{1}".format(name, str(args[0]))])
                return func(self, *args, **kwargs)
            else:
                return func(self, *args, **kwargs)
        return __wrapper
    return _wrapper
