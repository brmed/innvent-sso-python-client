# coding: utf-8
from mock import patch

from django.test import TestCase

from ..utils import SSOAPIClient
from ..forms import SSOUserCreationForm, SSOUserChangeForm, SSOPasswordChangeForm


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
        mocked_api_call.assert_called_once_with(**call_kwargs)
