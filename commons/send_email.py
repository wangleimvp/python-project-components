# !/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import mimetypes
import os
import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

__author__ = 'Aaron'


class EmailService(object):
    def __init__(self):
        self.mail_name = ""
        self.mail_user = ""
        self.mail_pass = ""
        self.mail_host = ""
        self.mail_postfix = ""
        self.mail_from = ("%s <" + self.mail_user + ">") % (Header(self.mail_name, 'utf-8'))

    def send_email(self, mail_list, subject, content, file_path=None):
        try:
            message = MIMEMultipart()
            message.attach(MIMEText(content, _charset='utf-8'))
            message["Subject"] = Header(subject, 'utf-8')
            message["From"] = self.mail_from
            message["To"] = ";".join(mail_list)
            message["Accept-Language"] = "zh-CN"
            message["Accept-Charset"] = "ISO-8859-1,utf-8"
            if file_path is not None and os.path.exists(file_path):
                c_type, encoding = mimetypes.guess_type(file_path)
                if c_type is None or encoding is not None:
                    c_type = "application/octet-stream"
                maintype, subtype = c_type.split("/", 1)
                with open(file_path, "rb") as f:
                    attachment = MIMEText(f.read(), subtype, 'utf-8')
                attachment.add_header("Content-Type", c_type)
                attachment.add_header("Content-Disposition", "attachment", filename=os.path.basename(file_path))
                message.attach(attachment)
            smtp = smtplib.SMTP()
            smtp.connect(self.mail_host)
            smtp.login(self.mail_user, self.mail_pass)
            smtp.sendmail(self.mail_from, mail_list, message.as_string())
            smtp.quit()
            return True
        except Exception, errmsg:
            logging.exception(errmsg)
            return False

