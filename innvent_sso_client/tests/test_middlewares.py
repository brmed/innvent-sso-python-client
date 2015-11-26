# coding: utf-8
import base64
import json
from datetime import datetime, timedelta
from model_mommy import mommy

from django.conf import settings
from django.contrib.auth import SESSION_KEY, get_user_model, login, logout, authenticate
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ImproperlyConfigured
from django.test import RequestFactory
from django.utils.importlib import import_module

from .testtools import TestCase
from ..middlewares import SSOMiddleware, SSORequestFromSettingsMiddleware


class SSOMiddlewareTestCase(TestCase):
    app_slug = 'app_slug'

    def setUp(self):
        self.data = {
            'user': {
                'login': 'test',
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User',
                'applications': ['default']
            },
            'token': 'b0ad5e305aa8a10ebe955520b5bab907'
        }

        self.factory = RequestFactory()
        self.middleware = SSOMiddleware()

    def __get_url(self, data=None):
        url = 'http://testserver/foo/bar/'

        if data:
            json_data = json.dumps(data)
            b64_data = base64.urlsafe_b64encode(json_data)

            url = '{0}?data={1}'.format(url, b64_data)

        return url

    def __add_sso_token_info(self, request, expiration=None, token=None):
        if not expiration:
            expiration = datetime.now() + timedelta(days=1)

        if not token:
            token = self.data['token']

        request.session['SSO_TOKEN'] = token
        request.session['SSO_TOKEN_EXPIRATION'] = expiration.isoformat()
        request.SSO_APPLICATION_SLUG = self.app_slug

    def __create_user_and_log_it_in(self, request, token_expiration=None):
        if not token_expiration:
            token_expiration = datetime.now() + timedelta(days=1)

        username_kwargs = {get_user_model().USERNAME_FIELD: self.data['user']['login']}
        mommy.make(get_user_model(), **username_kwargs)

        user = authenticate(
            token=self.data['token'],
            expiration_datetime=token_expiration,
            username=self.data['user']['login']
        )

        login(request, user)

        return user

    def assertUserNotAuthenticated(self, request):
        self.assertNotIn(SESSION_KEY, request.session)

    def assertUserAuthenticated(self, request, user):
        self.assertIn(SESSION_KEY, request.session)
        self.assertEqual(request.session[SESSION_KEY], user.id)

    def test_middleware_requires_authentication_middleware(self):
        request = self.factory.get(self.__get_url(self.data))

        self.assertRaises(
            ImproperlyConfigured, self.middleware.process_request, request
        )

    def test_parse_data_returns_user_data_plus_token(self):
        request = self.factory.get(self.__get_url(self.data))

        token, user_data = self.middleware.extract_user_data(request)

        self.assertEqual(self.data['token'], token)
        self.assertEqual(self.data['user'], user_data)

    def test_does_not_log_user_in_if_there_is_no_token_in_session(self):
        request = self.factory.get(self.__get_url(self.data))
        self._build_session(request)
        request.user = AnonymousUser()

        self.middleware.process_request(request)

        self.assertUserNotAuthenticated(request)

    def test_does_not_log_user_in_if_data_token_is_different_from_session_token(self):
        request = self.factory.get(self.__get_url(self.data))
        self._build_session(request)
        self.__add_sso_token_info(request, token='mfw_i_dont_even')
        request.user = AnonymousUser()

        self.middleware.process_request(request)

        self.assertUserNotAuthenticated(request)

    def test_logs_user_in_if_data_is_correct_and_token_is_the_same_as_session(self):
        request = self.factory.get(self.__get_url(self.data))
        self._build_session(request)
        self.__add_sso_token_info(request)
        request.user = AnonymousUser()

        self.middleware.process_request(request)

        user = get_user_model().objects.all()[0]
        self.assertUserAuthenticated(request, user)

    def test_logged_in_user_should_stay_logged_in_if_token_is_not_expired(self):
        request = self.factory.get(self.__get_url(self.data))
        self._build_session(request)
        self.__add_sso_token_info(request)
        request.user = self.__create_user_and_log_it_in(request)

        self.middleware.process_request(request)

        user = get_user_model().objects.all()[0]
        self.assertUserAuthenticated(request, user)

    def test_user_with_an_expired_token_should_not_log_in(self):
        request = self.factory.get(self.__get_url(self.data))
        self._build_session(request)
        self.__add_sso_token_info(request, expiration=datetime.now() - timedelta(days=1))
        request.user = AnonymousUser()

        self.middleware.process_request(request)

        self.assertUserNotAuthenticated(request)

    def test_logged_in_user_with_an_expired_token_should_logout(self):
        request = self.factory.get(self.__get_url(self.data))
        self._build_session(request)

        expiration = datetime.now() - timedelta(days=1)
        self.__add_sso_token_info(request, expiration=expiration)
        request.user = self.__create_user_and_log_it_in(request, expiration)

        self.middleware.process_request(request)

        self.assertUserNotAuthenticated(request)

    def test_user_without_sso_token_and_data_should_not_login(self):
        request = self.factory.get(self.__get_url())
        self._build_session(request)
        self.__add_sso_token_info(request)
        request.user = self.__create_user_and_log_it_in(request)
        logout(request)

        self.middleware.process_request(request)

        self.assertUserNotAuthenticated(request)

    def test_logged_in_user_without_sso_token_and_data_should_stay_logged_in(self):
        request = self.factory.get(self.__get_url())
        self._build_session(request)
        self.__add_sso_token_info(request)
        request.user = self.__create_user_and_log_it_in(request)

        # DELETA O TOKEN
        request.user.ssousertoken.delete()
        del request.user.__dict__['_ssousertoken_cache']

        self.middleware.process_request(request)

        self.assertUserAuthenticated(request, request.user)

    def test_store_sso_application_permission_as_true_if_default_is_present(self):
        request = self.factory.get(self.__get_url(self.data))
        self._build_session(request)
        self.__add_sso_token_info(request)
        request.user = AnonymousUser()

        self.middleware.process_request(request)

        self.assertIn('SSO_APPLICATION_PERMISSION', request.session)
        self.assertTrue(request.session['SSO_APPLICATION_PERMISSION'])

    def test_store_sso_application_permission_as_true_if_current_application_is_present(self):
        self.data['user']['applications'] = [self.app_slug]
        request = self.factory.get(self.__get_url(self.data))
        self._build_session(request)
        self.__add_sso_token_info(request)
        request.user = AnonymousUser()

        self.middleware.process_request(request)

        self.assertIn('SSO_APPLICATION_PERMISSION', request.session)
        self.assertTrue(request.session['SSO_APPLICATION_PERMISSION'])

    def test_store_sso_application_permission_as_false_if_neither_current_or_default_are_present(self):
        self.data['user']['applications'] = []
        request = self.factory.get(self.__get_url(self.data))
        self._build_session(request)
        self.__add_sso_token_info(request)
        request.user = AnonymousUser()

        self.middleware.process_request(request)

        self.assertIn('SSO_APPLICATION_PERMISSION', request.session)
        self.assertFalse(request.session['SSO_APPLICATION_PERMISSION'])


class SSORequestFromSettingsMiddlewareTests(TestCase):

    def setUp(self):
        self.url = 'http://testserver/foo/bar/'
        self.factory = RequestFactory()
        self.middleware = SSORequestFromSettingsMiddleware()

    def test_populates_request_with_settings_sso_application_slug(self):
        self.assertTrue(settings.SSO_APPLICATION_SLUG)
        request = self.factory.get(self.url)
        self.assertIsNone(getattr(request, 'SSO_APPLICATION_SLUG', None))

        self.middleware.process_request(request)

        self.assertEqual(settings.SSO_APPLICATION_SLUG, request.SSO_APPLICATION_SLUG)
