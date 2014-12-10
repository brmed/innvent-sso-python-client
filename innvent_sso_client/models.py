# coding:utf-8
from datetime import datetime

from django.conf import settings
from django.db import models


class SSOUserTokenManager(models.Manager):

    def create_or_update(self, user, token, expiration_datetime):
        qs = self.get_query_set()

        try:
            user_token = qs.get(user=user)
        except self.model.DoesNotExist:
            user_token = SSOUserToken(user=user)

        user_token.token = token
        user_token.expiration_datetime = expiration_datetime
        user_token.save()

        return user_token


class SSOUserToken(models.Model):
    objects = SSOUserTokenManager()

    token = models.CharField(max_length=32, unique=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    expiration_datetime = models.DateTimeField()
    last_modified = models.DateTimeField(auto_now=True)

    @property
    def has_expired(self):
        return datetime.now() > self.expiration_datetime
