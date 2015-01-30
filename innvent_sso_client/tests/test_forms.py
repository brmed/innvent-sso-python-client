# coding: utf-8
from mock import patch
from model_mommy import mommy

from django.contrib.auth import get_user_model
from django.test import TestCase

from ..utils import SSOAPIClient
from ..forms import SSOUserCreationForm, SSOUserChangeForm, SSOSetPasswordForm, SSOPasswordChangeForm


class SSOUserCreationFormTestCase(TestCase):

    @patch.object(SSOAPIClient, 'create_or_update_user')
    def test_calls_sso_api_client_correctly(self, mocked_api_call):
        data = {
            'username': 'foo',
            'password1': 'bar',
            'password2': 'bar',
        }

        form = SSOUserCreationForm(data)
        self.assertTrue(form.is_valid())
        form.save()

        call_kwargs = {
            'username': 'foo',
            'password': 'bar',
            'first_name': '',
            'last_name': '',
            'email': '',
        }
        mocked_api_call.assert_called_once_with(**call_kwargs)


class SSOUserChangeFormTestCase(TestCase):

    @patch.object(SSOAPIClient, 'update_user')
    def test_calls_sso_api_client_correctly(self, mocked_api_call):
        user = mommy.make(get_user_model(), username='foo')
        form = SSOUserChangeForm(instance=user)
        data = form.initial.copy()
        data.update({
            'first_name': 'name',
            'last_name': 'last_name',
            'email': 'email@email.com',
        })

        form = SSOUserChangeForm(data, instance=user)
        self.assertTrue(form.is_valid())
        form.save()

        call_kwargs = {
            'username': 'foo',
            'first_name': 'name',
            'last_name': 'last_name',
            'email': 'email@email.com',
        }
        mocked_api_call.assert_called_once_with(**call_kwargs)


class SSOSetPasswordFormTestcase(TestCase):

    @patch.object(SSOAPIClient, 'update_user')
    def test_calls_sso_api_client_correctly(self, mocked_api_call):
        user = mommy.make(get_user_model())
        data = {'new_password1': 'foo', 'new_password2': 'foo'}

        form = SSOSetPasswordForm(user, data)
        self.assertTrue(form.is_valid())
        form.save()

        call_kwargs = {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'password': 'foo',
        }
        mocked_api_call.assert_called_once_with(**call_kwargs)


class SSOPasswordChangeFormTestcase(TestCase):

    @patch.object(SSOAPIClient, 'update_user')
    def test_calls_sso_api_client_correctly(self, mocked_api_call):
        user = mommy.make(get_user_model())
        user.set_password('old')
        user.save()
        data = {'new_password1': 'foo', 'new_password2': 'foo', 'old_password': 'old'}

        form = SSOPasswordChangeForm(user, data)
        self.assertTrue(form.is_valid())
        form.save()

        call_kwargs = {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'password': 'foo',
        }
        mocked_api_call.assert_called_once_with(**call_kwargs)
