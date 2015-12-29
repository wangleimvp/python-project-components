#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import yaml

__author__ = 'wanglei'


class WeixinTemplateBuilder(object):

    _weixin_config = None
    _templates = None
    run_mode = 'preprod'

    @classmethod
    def get_template_by_name(cls, name='default'):
        if cls._templates is None or cls._templates.get(name, None) is None:
            if cls._templates is None:
                cls._templates = dict()
            if cls._weixin_config is None:
                with file(os.path.join(os.getcwd(), 'weixin_templates.yaml'), 'r') as file_stream:
                    cls._weixin_config = yaml.load(file_stream).get(cls.run_mode)
            weixin_config = cls._weixin_config.get(name)
            if weixin_config is not None:
                cls._templates[name] = weixin_config
        return cls._templates[name]
