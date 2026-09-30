# coding: utf-8
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, SetPasswordForm, PasswordChangeForm

from django.forms import ValidationError

from .utils import SSOAPIClient, SSOPasswordPolicyError


class SSOPasswordPolicyErrorsMixin(object):
    password_error_field = 'new_password1'
    password_error_fields_by_rule = {}

    def add_password_policy_errors(self, error):
        violations = error.violations or [{'message': error.message}]

        for violation in violations:
            field = self.password_error_fields_by_rule.get(
                violation.get('rule'), self.password_error_field
            )
            self.add_field_error(field, violation.get('message') or error.message)

    def add_field_error(self, field, message):
        self._errors.setdefault(field, self.error_class()).append(message)
        self.cleaned_data.pop(field, None)


class SSOUserCreationForm(SSOPasswordPolicyErrorsMixin, UserCreationForm):
    password_error_field = 'password1'

    def clean(self):
        cleaned_data = super(SSOUserCreationForm, self).clean()

        if self._errors:
            return cleaned_data

        try:
            SSOAPIClient().create_or_update_user(
                username=cleaned_data.get('username'),
                password=cleaned_data.get('password1'),
                first_name=cleaned_data.get('first_name', ''),
                last_name=cleaned_data.get('last_name', ''),
                email=cleaned_data.get('email', ''),
            )
        except SSOPasswordPolicyError as error:
            self.add_password_policy_errors(error)

        return cleaned_data


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


class SSOUpdatePasswordByIdMixin(SSOPasswordPolicyErrorsMixin):

    def clean(self):
        cleaned_data = super(SSOUpdatePasswordByIdMixin, self).clean()

        if self._errors:
            return cleaned_data

        try:
            self.update_sso_password(cleaned_data['new_password1'])
        except SSOPasswordPolicyError as error:
            self.add_password_policy_errors(error)

        return cleaned_data

    def update_sso_password(self, password):
        sso_client = SSOAPIClient()
        sso_user = sso_client.get_user(self.user.username)
        sso_client.update_user_by_id(sso_user['id'], password=password)


class SSOSetPasswordForm(SSOUpdatePasswordByIdMixin, SetPasswordForm):
    """
    Let the user change his/her password without entering the
    old password.
    """


class SSOPasswordChangeForm(SSOPasswordPolicyErrorsMixin, PasswordChangeForm):
    """
    Let the user change his/her password "only" by entering his/her
    old password.
    """
    password_error_fields_by_rule = {'current_password': 'old_password'}

    def __init__(self, *args, **kwargs):
        super(SSOPasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].label = u'Senha atual'

    def clean_old_password(self):
        return self.cleaned_data['old_password']

    def clean(self):
        cleaned_data = super(SSOPasswordChangeForm, self).clean()

        if self._errors:
            return cleaned_data

        try:
            SSOAPIClient().change_own_password(
                self.user.username,
                cleaned_data['old_password'],
                cleaned_data['new_password2'],
            )
        except SSOPasswordPolicyError as error:
            self.add_password_policy_errors(error)

        return cleaned_data


class SSORecoverPasswordForm(SSOUpdatePasswordByIdMixin, SetPasswordForm):
    """
    Let the user change his/her password without entering the
    old password, but the new password must be different from
    the old one.
    """
    def clean(self):
        self.__validate_password()
        return super(SSORecoverPasswordForm, self).clean()

    def __validate_password(self):
        new_password = self.cleaned_data.get('new_password2')
        if new_password and SSOAPIClient().check_user_identity(self.user.username, new_password):
            raise ValidationError("Você não pode utilizar uma senha que já utilizou antes.")
