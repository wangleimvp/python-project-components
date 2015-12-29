#!/usr/bin/env python
# -*- coding: utf-8 -*-
import inspect

from datetime import date
from datetime import datetime
from decorated.base.dict import DefaultDict

from commons import jsonutil

__author__ = 'freeway'


class Attribute(object):
    """
    example:

    class Test1BO(BizModel):
        bar = Attribute(attri_type=str)

    class Test2BO(BizModel):

        foo = Attribute(attri_type=str)
        tests = Attribute(attri_type=list, generic_type=Test1BO)
        test = Attribute(attri_type=Test1BO)
    """

    def __init__(self, default=None, attri_type=None,
                 datetime_fmt='%Y-%m-%d %H:%M:%S', date_fmt='%Y-%m-%d',
                 generic_type=None, split=" ", prefix=None, exclude=False, validators=None):
        """

        :param default: 默认值
        :type default:
        :param attri_type: 属性对应的类型
        :type attri_type:
        :param datetime_fmt: 在执行attributes的时候会转换成 datetime_fmt 的格式化的字串
        :type datetime_fmt: str
        :param date_fmt: 在执行attributes的时候会转换成 date_fmt 的格式化的字串
        :type date_fmt: str
        :param generic_type: 集合中的类型，例如：Attribute(attri_type=list, generic_type=Test1BO)
        :type generic_type:
        :param split: 用于attri_type=list， generic_type=str这种情况
        :type split: str
        :param prefix: 字符类型前面可以加入的前缀
        :type prefix: str
        :param exclude: 在执行attributes的时候排除掉这个属性
        :type exclude: bool
        :param validators: 校验器
        :type validators: app.commons.validator.Validators
        :return:
        :rtype:
        """
        super(Attribute, self).__init__()

        self.datetime_fmt = datetime_fmt
        self.date_fmt = date_fmt
        self.attri_type = attri_type
        self.generic_type = generic_type

        self.prefix = prefix
        self.exclude = exclude
        # 用于字符串和list的互转
        self.split = split
        self.validators = validators
        if attri_type == list:
            self.default = []
        elif attri_type == tuple:
            self.default = tuple()
        else:
            self.default = default


class BizModel(object):
    def __repr__(self):
        return u'<%s %s>' % (self.__class__.__name__, self.attributes)

    @classmethod
    def class_attributes(cls):
        """

        :return:
        :rtype: tuple[str, Attribute]
        """
        return get_biz_model_class_attributes(cls)

    def __init__(self, **kwargs):
        super(BizModel, self).__init__()
        self.class_attributes = get_biz_model_class_attributes(self.__class__)
        for name, obj in self.class_attributes:
            setattr(self, name, self.value_converter(obj, kwargs[name]) if name in kwargs else obj.default)

    def validate(self, is_validate_all=False, is_prepend_name=True):
        """ 验证对象是否合法

        :param is_validate_all:
        :type is_validate_all:
        :param is_prepend_name:
        :type is_prepend_name:
        :return:
        :rtype:
        """
        from serviceBO.validator import Required

        errors = DefaultDict()
        for name, attribute in self.class_attributes:
            if (not is_validate_all) and len(errors) > 0:
                break
            valids = attribute.validators
            if valids:
                validators = valids.validators
                for idx, validator in enumerate(validators):
                    if isinstance(validator, Required):
                        if not validator(getattr(self, name)):
                            errors[name] = self._get_error_message(is_prepend_name, validator, valids.name)
                            break
                        continue
                    else:
                        value = getattr(self, name)
                        if value is None or str(value).strip() == '':
                            break
                        if hasattr(validator, "field"):
                            if validator.field:
                                if not validator(getattr(self, name), getattr(self, validator.field)):
                                    errors[name] = self._get_error_message(is_prepend_name, validator, valids.name)
                                    break
                            else:
                                if not validator(getattr(self, name), None):
                                    errors[name] = self._get_error_message(is_prepend_name, validator, valids.name)
                                    break
                        else:
                            if not validator(getattr(self, name)):
                                errors[name] = self._get_error_message(is_prepend_name, validator, valids.name)
                                break
        return errors

    @classmethod
    def gen_validator_rules(cls):
        """ 生成校验 规则
        :return:
        :rtype: dict
        """
        rules = DefaultDict()
        for name, attribute in cls.class_attributes():
            valids = attribute.validators
            if valids:
                validators = valids.validators

                for validator in validators:
                    rule = DefaultDict()
                    if not rules[name]:
                        rules[name] = []
                    rules[name].append(rule)
                    rule_name = validator.__class__.__name__
                    rule["rule"] = rule_name
                    for key in dir(validator):
                        if key == "message":
                            rule[key] = "“{0}”{1}".format(valids.name, validator.message) \
                                if valids.name else validator.message
                            continue
                        try:
                            if (not key.startswith("_")) and key != "priority" and (not key.startswith("VALID")):
                                value = getattr(validator, key)
                            else:
                                continue
                        except AttributeError:
                            continue
                        rule[key] = value
        return rules

    def _get_error_message(self, add_name, validator, name):
        return "“{0}”{1}".format(name, validator.message) if add_name else validator.message

    @staticmethod
    def value_converter(attribute, val):
        vt = type(val)  # 为了效率 简单粗暴
        v = val
        if attribute.attri_type is not None and attribute.attri_type != str:
            if val is None or val == '':
                v = attribute.default
            elif attribute.attri_type == unicode:
                if vt != unicode:
                    v = str(val).encode('utf-8')
            elif attribute.attri_type == bool:
                if vt == str or vt == unicode:
                    if len(val.strip()) > 0:
                        v = bool(int(v))
                    else:
                        v = None
            elif attribute.attri_type == datetime:
                if vt == str or vt == unicode:
                    if len(val.strip()) > 0:
                        v = datetime.strptime(val, attribute.datetime_fmt)
                    else:
                        v = None
            elif attribute.attri_type == date:
                if vt == str or vt == unicode:
                    if len(val.strip()) > 0:
                        v = datetime.strptime(val, attribute.date_fmt).date()
                    else:
                        v = None
            elif attribute.attri_type in (list, tuple):
                if attribute.generic_type and issubclass(attribute.generic_type, BizModel):
                    v = list()
                    if isinstance(val, basestring):
                        val = jsonutil.json_decode(val)

                    for data in val:
                        v.append(attribute.generic_type(**data))

                else:
                    if isinstance(val, basestring):
                        v = val.strip().split(attribute.split) if len(val.strip()) > len(attribute.split) else []
                    else:
                        v = attribute.attri_type(val)

                if attribute.attri_type == tuple and (not isinstance(v, tuple)):
                    v = tuple(v)
            elif issubclass(attribute.attri_type, BizModel):
                if isinstance(val, basestring):
                    v = attribute.attri_type(**jsonutil.json_decode(val))
                else:
                    v = attribute.attri_type(**val)
            else:
                v = attribute.attri_type(val)
        return v

    def update(self, kwargs):
        for name, obj in self.class_attributes:
            if name in kwargs:
                setattr(self, name, self.value_converter(obj, kwargs[name]))
        return self

    @property
    def attributes(self):
        """ 在bo转vo的时候使用

        :return:
        """
        d = DefaultDict()
        for name, obj in self.class_attributes:
            if obj.exclude:
                continue
            value = getattr(self, name)
            if isinstance(value, BizModel):
                d[name] = value.attributes
            elif isinstance(value, (list, tuple)):
                values = []
                for v in value:
                    if isinstance(v, BizModel):
                        values.append(v.attributes)
                    else:
                        if isinstance(v, basestring) and obj.prefix and len(v.strip()) > 0 and (not v.startswith(obj.prefix)):
                            v = obj.prefix + v
                        values.append(v)
                d[name] = tuple(values) if isinstance(value, tuple) else values
            else:
                v = getattr(self, name)
                if isinstance(v, basestring) and obj.prefix and len(v.strip()) > 0 and (not v.startswith(obj.prefix)):
                    v = obj.prefix + v
                d[name] = v
        return d

    @property
    def flat_attributes(self):
        """ 扁平化的属性，只保留一层。
        在bo转dbmodel使用
        如果存在list就把list转换成字符串
        如果是bo对象，就把这个对象转换成json字符串
        :return:
        """
        d = DefaultDict()
        for name, obj in self.class_attributes:
            value = getattr(self, name)
            if isinstance(value, BizModel):
                d[name] = jsonutil.json_encode(value.attributes)
            elif isinstance(value, (list, tuple)):
                if obj.generic_type and issubclass(obj.generic_type, BizModel):
                    values = []
                    for v in value:
                        values.append(v.attributes)
                    d[name] = jsonutil.json_encode(values)
                else:
                    values = []
                    for v in value:
                        if isinstance(v, basestring) and obj.prefix:
                            if v.startswith(obj.prefix):
                                v = v.replace(obj.prefix, '', 1)
                            values.append(v)
                        else:
                            values.append(v)
                    d[name] = obj.split.join(values)
            else:
                v = getattr(self, name)
                if isinstance(v, basestring) and obj.prefix:
                    if v.startswith(obj.prefix):
                        v = v.replace(obj.prefix, '', 1)
                d[name] = v
        return d


def get_biz_model_class_attributes(cls):
    return [(class_attr[0], class_attr[3])
            for class_attr in inspect.classify_class_attrs(cls)
            if isinstance(class_attr[3], Attribute)]
