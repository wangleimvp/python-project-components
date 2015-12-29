#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import random
import string

import yaml
from oss.oss_api import OssAPI

from commons import stringutil

__author__ = 'freeway'


class UploadFactory(object):
    """
    memory cache factory
    """

    _oss_configs = None
    _oss_dict = dict()
    run_mode = 'development'

    def __init__(self, regional_node=None, id=None, key=None, bucket=None,
                 download_site=None, download_image_site=None, image_prefix=None, image_max_length=4194304):
        self.regional_node = regional_node
        self.id = id
        self.key = key
        self.bucket = bucket
        self.download_site = download_site
        self.download_image_site = download_image_site
        self.image_prefix = image_prefix
        self.image_max_length = image_max_length

        self.download_image_prefix = download_image_site + image_prefix



    @classmethod
    def get_instance(cls, name='default'):
        if not cls._oss_configs:
            with file(os.path.join(os.getcwd(), 'oss_config.yaml'), 'r') as file_stream:
                yml = yaml.load(file_stream)
            cls._oss_configs = yml.get(cls.run_mode)

        upload_factory = cls._oss_dict.get(name, None)
        if upload_factory:
            return upload_factory

        oss_config = cls._oss_configs.get(name)
        if oss_config:
            upload_factory = UploadFactory(regional_node=oss_config.get('regional_node'),
                                           id=oss_config.get('id'),
                                           key=oss_config.get('key'),
                                           bucket=oss_config.get('bucket'),
                                           download_site=oss_config.get('download_site'),
                                           download_image_site=oss_config.get('download_image_site'),
                                           image_prefix=oss_config.get('image_prefix'),
                                           image_max_length=oss_config.get('image_max_length'))
            cls._oss_dict[name] = upload_factory
            return upload_factory
        else:
            return None

    def upload_file_form_data(self, file_data, file_path, content_type=None):
        """ 上传文件到oss服务器上

        :param file_data: 文件的数据
        :param file_path: 保存到OSS的路径
        :param content_type: 上下文类型
        :return: 上传成功返回true
        """
        oss = OssAPI(self.regional_node, self.id, self.key)
        if content_type:
            res = oss.put_object_from_string(self.bucket, file_path, file_data, content_type=content_type)
        else:
            res = oss.put_object_from_string(self.bucket, file_path, file_data)
        if 200 == res.status:
            return True
        else:
            res_message = "OSS ERROR\n%s\n%s" % (res.status, res.read())
            logging.info(res_message)
            return False

    def upload_file_from_fp(self, fp, file_path, content_type=None, headers=None):
        """上传文件到oss服务器上

        :param file_data: 文件的数据
        :param file_path: 保存到OSS的路径
        :return:
        """
        oss = OssAPI(self.regional_node, self.id, self.key)
        if content_type:
            res = oss.put_object_from_fp(self.bucket, file_path, fp, content_type=content_type, headers=headers)
        else:
            res = oss.put_object_from_fp(self.bucket, file_path, fp, headers=headers)
        if 200 == res.status:
            return True
        else:
            res_message = "OSS ERROR\n%s\n%s" % (res.status, res.read())
            logging.info(res_message)
            return False

    def delete_file(self, file_path):
        """ 删除远程服务端的文件

        :param file_path: 文件路径
        :return:
        """
        try:
            oss = OssAPI(self.regional_node, self.id, self.key)
            res = oss.delete_object(self.bucket, file_path)
        except Exception as e:
            return False
        return 204 == res.status

    @staticmethod
    def generate_image_url(index, image_size, url_prefix='', image_extension='jpg'):
        """ 图片大小

        :param image_size: 图片长宽
        :param url_prefix: url前缀
        :return: 图片id 和 图片url
        """
        image_id = index
        one_path = stringutil.base62_encode(divmod(image_id, 100)[1])
        two_path = stringutil.base62_encode(divmod(image_id / 100, 1000)[1])
        random_str = ''.join(random.sample(string.ascii_letters + string.digits, 2))

        image_url = url_prefix + one_path + '/' + two_path + '/' + random_str + "_" + \
                    stringutil.base62_encode(image_id) + "_" + \
                    str(image_size[0]) + "x" + str(image_size[1]) + "." + image_extension

        return image_url
