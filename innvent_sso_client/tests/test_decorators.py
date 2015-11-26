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
        self.request.session['SSO_APPLICATION_PERMISSION'] = True

    def test_should_redirect_to_login_path_of_settings_sso_host(self):
        with vcr.use_cassette('access_token_valid.json'):
            token = SSOAPIClient().retrieve_new_token()['token']

        qs = QueryDict(None, mutable=True)
        qs['callback_url'] = 'http://testserver{0}'.format(self.url)
        qs['token'] = token

        expected_url = '{0}?{1}'.format(
            sso_hostname('/authorize'), qs.urlencode(safe='/')
        )

        with self.settings(SSO_CALLBACK_PATH=None):
            with vcr.use_cassette('access_token_valid.json'):
                response = view(self.request)

        self.assertEqual(302, response.status_code)
        self.assertEqual(expected_url, response['Location'])

    def test_should_redirect_to_login_path_of_settings_sso_host_with_callback_on_settings(self):
        with vcr.use_cassette('access_token_valid.json'):
            token = SSOAPIClient().retrieve_new_token()['token']

        qs = QueryDict(None, mutable=True)
        callback_path = '/callback_url/'
        qs['callback_url'] = 'http://testserver{0}'.format(callback_path)
        qs['token'] = token

        expected_url = '{0}?{1}'.format(
            sso_hostname('/authorize'), qs.urlencode(safe='/')
        )

        with self.settings(SSO_CALLBACK_PATH=callback_path):
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

    @patch.object(AnonymousUser, 'is_authenticated', Mock(return_value=True))
    def test_should_redirect_user_to_forbidden_page_if_sso_application_permission_is_false(self):
        self.request.session['SSO_APPLICATION_PERMISSION'] = False

        response = view(self.request)

        self.assertEqual(302, response.status_code)

        expected_url = reverse('forbidden_application')
        self.assertEqual(expected_url, response['Location'])

    @patch.object(AnonymousUser, 'is_authenticated', Mock(return_value=True))
    def test_should_not_redirect_user_to_forbidden_if_sso_check_application_permission_is_false(self):
        self.request.session['SSO_APPLICATION_PERMISSION'] = False

        with self.settings(SSO_CHECK_APPLICATION_PERMISSION=False):
            response = view(self.request)

        self.assertEqual(200, response.status_code)
        self.assertEqual('OK', response.content)
