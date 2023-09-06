# coding: utf-8
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, SetPasswordForm, PasswordChangeForm

from django.forms import ValidationError

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
        sso_client = SSOAPIClient()
        sso_user = sso_client.get_user(user.username)
        sso_client.update_user_by_id(
            sso_user['id'],
            login=user.username,
            firstname=user.first_name,
            lastname=user.last_name,
            email=user.email,
            is_active=user.is_active
        )
        return user


class SSOSetPasswordForm(SetPasswordForm):
    """
    Let the user change his/her password without entering the
    old password.
    """
    def save(self, commit=True):
        sso_client = SSOAPIClient()
        sso_user = sso_client.get_user(self.user.username)
        sso_client.update_user_by_id(
            sso_user['id'],
            login=self.user.username,
            password=self.cleaned_data['new_password1'],
            firstname=self.user.first_name,
            lastname=self.user.last_name,
            email=self.user.email,
        )

        return super(SSOSetPasswordForm, self).save(commit)


class SSOPasswordChangeForm(PasswordChangeForm):
    """
    Let the user change his/her password "only" by entering his/her
    old password.
    """
    def clean_old_password(self):
        old_password = self.cleaned_data["old_password"]
        if not SSOAPIClient().check_user_identity(self.user.username, old_password):
            raise ValidationError(
                self.error_messages['password_incorrect'])
        return old_password

    def clean(self):
        cleaned_data = super(SSOPasswordChangeForm, self).clean()
        self.__validate_password()
        return cleaned_data

    def __validate_password(self):
        new_password = self.cleaned_data.get('new_password2')
        old_password = self.cleaned_data.get('old_password')
        if new_password and old_password and new_password == old_password:
            raise ValidationError("Você não pode utilizar uma senha que já utilizou antes.")


    def save(self, commit=True):
        sso_client = SSOAPIClient()
        user_sso = sso_client.get_user(self.user.username)
        sso_client.update_user_by_id(
            user_sso['id'],
            login=self.user.username,
            password=self.cleaned_data['new_password1'],
            firstname=self.user.first_name,
            lastname=self.user.last_name,
            email=self.user.email,
        )

        return super(SSOPasswordChangeForm, self).save(commit)


class SSORecoverPasswordForm(SetPasswordForm):
    """
    Let the user change his/her password without entering the
    old password, but the new password must be different from
    the old one.
    """
    def clean(self):
        cleaned_data = super(SSORecoverPasswordForm, self).clean()
        self.__validate_password()
        return cleaned_data

    def __validate_password(self):
        new_password = self.cleaned_data.get('new_password2')
        if SSOAPIClient().check_user_identity(self.user.username, new_password):
            raise ValidationError("Você não pode utilizar uma senha que já utilizou antes.")

    def save(self, commit=True):
        sso_client = SSOAPIClient()
        user_sso = sso_client.get_user(self.user.username)
        sso_client.update_user_by_id(
            user_sso['id'],
            login=self.user.username,
            password=self.cleaned_data['new_password1'],
            firstname=self.user.first_name,
            lastname=self.user.last_name,
            email=self.user.email,
        )

        return super(SSORecoverPasswordForm, self).save(commit)