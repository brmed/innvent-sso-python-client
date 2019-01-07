# coding: utf-8
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, SetPasswordForm, PasswordChangeForm

from .utils import SSOAPIClient


class SSOUserCreationForm(UserCreationForm):

    def save(self, commit=True):
        user = super(SSOUserCreationForm, self).save(commit)

        SSOAPIClient().create_or_update_user(
            username=user.username,
            password=self.cleaned_data['password1'],
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
        )

        return user


class SSOUserChangeForm(UserChangeForm):

    def save(self, commit=True):
        user = super(SSOUserChangeForm, self).save(commit)

        SSOAPIClient().update_user(
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
        )

        return user


class SSOSetPasswordForm(SetPasswordForm):

    def save(self, commit=True):
        SSOAPIClient().update_user(
            username=self.user.username,
            password=self.cleaned_data['new_password1'],
            first_name=self.user.first_name,
            last_name=self.user.last_name,
            email=self.user.email,
        )

        return super(SSOSetPasswordForm, self).save(commit)


class SSOPasswordChangeForm(PasswordChangeForm):
    def clean_old_password(self):
        old_password = self.cleaned_data["old_password"]
        if not SSOAPIClient().check_user_identity(self.user.username, old_password):
            from django.forms import ValidationError
            raise ValidationError(
                self.error_messages['password_incorrect'])
        return old_password

    def save(self, *args, **kwargs):
        SSOAPIClient().update_user(
            username=self.user.username,
            password=self.cleaned_data['new_password1'],
            first_name=self.user.first_name,
            last_name=self.user.last_name,
            email=self.user.email,
        )

        return super(SSOPasswordChangeForm, self).save(*args, **kwargs)
