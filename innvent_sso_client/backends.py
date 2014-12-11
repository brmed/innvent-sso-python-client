# coding: utf-8
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from models import SSOUserToken


class SSOBackend(ModelBackend):

    def authenticate(self, token=None, expiration_datetime=None, username=None, **kwargs):
        UserModel = get_user_model()
        username_kwargs = {UserModel.USERNAME_FIELD: username}

        try:
            user = UserModel.objects.get(**username_kwargs)
        except UserModel.DoesNotExist:
            user = UserModel.objects.create(
                email=kwargs.get('email', ''),
                first_name=kwargs.get('first_name', ''),
                last_name=kwargs.get('last_name', ''),
                **username_kwargs
            )

        user.backend = 'innvent_sso_client.backends.SSOBackend'

        SSOUserToken.objects.create_or_update(user, token, expiration_datetime)

        return user
