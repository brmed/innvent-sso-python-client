# coding:utf-8
from datetime import datetime

from django.conf import settings
from django.db import models


class SSOUserToken(models.Model):

    token = models.CharField(max_length=32, unique=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    expiration_datetime = models.DateTimeField()
    last_modified = models.DateTimeField(auto_now=True)

    @property
    def has_expired(self):
        return datetime.now() > self.expiration_datetime
