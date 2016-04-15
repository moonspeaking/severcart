# -*- coding:utf-8  -*-

from django.db import models

class Settings(models.Model):
    
    # настройка подключения к серверу электронной почты
    smtp_server   = models.CharField(max_length=256, null=True)
    smtp_port     = models.IntegerField(db_index=True, null=True)
    email_sender  = models.EmailField(max_length=254, null=True, blank=True)
    smtp_login    = models.CharField(max_length=256, null=True)
    smtp_password = models.CharField(max_length=256, null=True)
    use_ssl       = models.NullBooleanField(null=True)
    use_tls       = models.NullBooleanField(null=True)

    # настройки формата печатаемых наклеек
    # принимает значения A4, A5, ...
    page_format  =  models.CharField(max_length=2, null=True)
