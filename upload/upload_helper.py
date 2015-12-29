#!/usr/bin/env python
# -*- coding: utf-8 -*-
import StringIO
import logging
import tempfile
from PIL import Image
from PIL.ExifTags import TAGS
import datetime
from tornado.httputil import format_timestamp
from service_bo.base_service import ServiceException, ServiceError
from upload_factory import UploadFactory
from app.services.image_service import ImageService

__author__ = 'freeway'


class UploadHelper(object):
    """ 文件上传帮助类

    """

    _image_content_type_dict = {'gif': 'image/gif', 'jpg': 'image/jpeg', 'bmp': 'image/bmp',
                                'png': 'image/png'}

    @classmethod
    def get_download_image_site(cls, name='default'):
        return UploadFactory.get_instance(name).download_image_site

    @classmethod
    def get_download_site(cls, name='default'):
        return UploadFactory.get_instance(name).download_site

    @classmethod
    def upload_image(cls, file_data, save_extension="jpg"):
        """ 上传图片

        :param file_data:
        :param save_extension: 保存成什么格式的问题
        :return: 上传后的路径
        """
        content_type = cls._image_content_type_dict.get(save_extension, None)
        if not content_type:
            raise ServiceException(20201, 'image format is not support')

        upload_factory = UploadFactory.get_instance('default')
        if len(file_data) > upload_factory.image_max_length:
            raise ServiceException(20202, 'beyond the image file maximum size')
        # 名虽然是图片格式，但内容并非是图片。
        with tempfile.NamedTemporaryFile(suffix="."+save_extension, delete=True) as tmp_file:
            try:
                with Image.open(StringIO.StringIO(file_data)) as image:

                    if hasattr( image, '_getexif' ):
                        exifinfo = image._getexif()
                        if exifinfo != None:
                            for tag, value in exifinfo.items():
                                decoded = TAGS.get(tag, tag)
                                log_str = 'decoded:' + str(decoded) + ', value:' + str(value)
                                logging.info(log_str)

                    # 使用resize保障图片文件是一个真正的图片
                    image.resize(image.size)
                    image_service = ImageService()
                    image_id = image_service.generate_image_id()
                    image_url = upload_factory.generate_image_url(image_id,
                                                                  image.size,
                                                                  url_prefix=upload_factory.image_prefix,
                                                                  image_extension=save_extension)

                    logging.info(tmp_file.name)
                    image.save(tmp_file)

                    expires = format_timestamp(datetime.datetime.today() + datetime.timedelta(days=+360))
                    headers = {'expires': expires,
                               'Cache-Control': 'max-age=%s' % (360*24*60*60)}
                    is_success = upload_factory.upload_file_from_fp(tmp_file, image_url, content_type=content_type,
                                                                    headers=headers)
                    if is_success:
                        image_service.save(image_id, image_url)
                        return image_url
                    else:
                        raise ServiceError(1001, 'image file upload failure')
            except IOError as error:
                logging.exception(error)
                # 进行日志记录，因为这些操作大多数是破坏者的做法。
                raise ServiceException(20203, 'invalid image format')

    @classmethod
    def delete_image(cls, file_path):
        # 删除已经上传的图片
        upload_factory = UploadFactory.get_instance('default')
        is_success = upload_factory.delete_file(file_path)
        if is_success:
            image_service = ImageService()
            image_service.delete_by_image_url(file_path)