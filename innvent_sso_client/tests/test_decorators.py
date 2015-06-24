# coding: utf-8
from mock import patch, Mock

from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse
from django.http import HttpResponse, QueryDict
from django.test import RequestFactory

from .testtools import TestCase, vcr
from ..decorators import sso_required
from ..utils import sso_hostname, SSOAPIClient


@sso_required
def view(request):
    return HttpResponse('OK')


class SSORequiredTestCase(TestCase):

    def setUp(self):
        self.url = '/test/'
        self.request = RequestFactory().get(self.url)
        self.request.user = AnonymousUser()

        self._build_session(self.request)

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
            response = view(self.request)

        self.assertEqual(302, response.status_code)
        self.assertEqual(expected_url, response['Location'])

    @patch.object(AnonymousUser, 'is_authenticated', Mock(return_value=True))
    def test_should_not_redirect_for_logged_user(self):
        response = view(self.request)

        self.assertEqual(200, response.status_code)
        self.assertEqual('OK', response.content)

    def test_should_save_token_at_session(self):
        with vcr.use_cassette('access_token_valid.json'):
            response = view(self.request)

        with vcr.use_cassette('access_token_valid.json'):
            token_dict = SSOAPIClient().retrieve_new_token()

        session = self.request.session

        self.assertIn('SSO_TOKEN', session)
        self.assertEqual(session['SSO_TOKEN'], token_dict['token'])

        self.assertIn('SSO_TOKEN_EXPIRATION', session)
        self.assertEqual(session['SSO_TOKEN_EXPIRATION'], token_dict['expires_at'].isoformat())
