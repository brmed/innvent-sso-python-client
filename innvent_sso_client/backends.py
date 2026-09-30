# coding: utf-8
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from models import SSOUserToken, DuplicatedTokenException


class SSOBackend(ModelBackend):

    def authenticate(self, token=None, expiration_datetime=None, username=None, **kwargs):
        if not all((token, expiration_datetime, username)):
            return None

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
        else:
            self.sync_email(user, kwargs.get('email'))

        try:
            SSOUserToken.objects.create_or_update(user, token, expiration_datetime)

            return user
        except DuplicatedTokenException:
            return None

    def sync_email(self, user, email):
        if not email or email == user.email:
            return

        user.email = email
        user.save(update_fields=['email'])
