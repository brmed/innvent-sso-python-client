# coding: utf-8
from mock import patch, Mock

from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse
from django.http import QueryDict
from django.test import TestCase

from .testtools import vcr
from ..utils import sso_hostname, SSOAPIClient


class SSORequiredTestCase(TestCase):

    def setUp(self):
        self.url = reverse('sso_required')

    def test_should_redirect_to_login_path_of_settings_sso_host(self):
        with vcr.use_cassette('access_token_valid.json'):
            token = SSOAPIClient().retrieve_new_token()['token']

        qs = QueryDict(None, mutable=True)
        qs['callback_url'] = 'http://testserver{0}'.format(self.url)
        qs['token'] = token

        expected_url = '{0}?{1}'.format(
            sso_hostname('/authorize'), qs.urlencode(safe='/')
        )

        with vcr.use_cassette('access_token_valid.json'):
            response = self.client.get(self.url)

        self.assertEqual(302, response.status_code)
        self.assertEqual(expected_url, response['Location'])

    @patch.object(AnonymousUser, 'is_authenticated', Mock(return_value=True))
    def test_should_not_redirect_for_logged_user(self):
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)
        self.assertEqual('OK', response.content)

    def test_should_save_token_at_session(self):
        with vcr.use_cassette('access_token_valid.json'):
            response = self.client.get(self.url)

        with vcr.use_cassette('access_token_valid.json'):
            token_dict = SSOAPIClient().retrieve_new_token()

        session = self.client.session

        self.assertIn('SSO_TOKEN', session)
        self.assertEqual(session['SSO_TOKEN'], token_dict['token'])

        self.assertIn('SSO_TOKEN_EXPIRATION', session)
        self.assertEqual(session['SSO_TOKEN_EXPIRATION'], token_dict['expires_at'].isoformat())
