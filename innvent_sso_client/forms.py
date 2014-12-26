# coding: utf-8
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm

from .utils import SSOApiClient


class SSOUserCreationForm(UserCreationForm):

    def save(self, commit=True):
        user = super(SSOUserCreationForm, self).save(commit)

        SSOApiClient().create_user(
            username=self.user.username,
            password=self.cleaned_data['new_password1'],
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
        )

        return user




class SSOPasswordChangeForm(PasswordChangeForm):

    def save(self, commit=True):
        SSOApiClient().update_user(
            username=self.user.username,
            password=self.cleaned_data['new_password1'],
            first_name=self.user.first_name,
            last_name=self.user.last_name,
            email=self.user.email,
        )

        return super(SSOPasswordChangeForm, self).save(commit)
