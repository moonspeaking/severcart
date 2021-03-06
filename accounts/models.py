# -*- coding:utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser
from index.models import OrganizationUnits


class AnconUser(AbstractBaseUser):
    """
    Custom user class.
    Details: http://blackglasses.me/2013/09/17/custom-django-user-model/
    """
    username    = models.CharField(_('Login'), unique=True, db_index=True, max_length=64)
    departament = models.ForeignKey(OrganizationUnits, blank=True, null=True, verbose_name=_('Organization unit'))
    joined      = models.DateTimeField(auto_now_add=True)
    is_active   = models.BooleanField(default=True)
    is_admin    = models.BooleanField(default=False)
    fio         = models.CharField(_('Full name'), max_length=256, blank=True, null=True)
    email       = models.EmailField(max_length=254, null=True, blank=True)
    secret_key  = models.CharField(_('Secret key'), unique=True, db_index=True, max_length=64, null=True)
    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username
