# coding: utf-8
import unittest
from mock import patch, Mock
from urllib import urlencode

from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth import SESSION_KEY
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

from ..middlewares import SSOAuthenticationMiddleware


class SSOAuthenticationMiddlewareTestCase(unittest.TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = SSOAuthenticationMiddleware()

    def __get_url(self, key=''):
        return '/' if not key else '/?{0}'.format(urlencode({'token': key}))

    def assertNoLoggedUser(self, request):
        self.assertFalse(request.session.keys())

    def assertLoggedUser(self, request, user):
        self.assertEqual(request.session[SESSION_KEY], user.id)

    def test_middleware_requires_authentication_middleware(self):
        request = self.factory.get(self.__get_url())

        self.assertRaises(ImproperlyConfigured,
            self.middleware.process_request, request
        )

    @patch.object(AnonymousUser, 'is_authenticated', Mock(return_value=True))
    def test_keep_user_logged_if_no_token_was_provided_and_has_not_expired(self):
        request = self.factory.get(self.__get_url())
        user = AnonymousUser()
        self.middleware.process_request(request)
        self.assertLoggedUser(request, user)


"""
#################################################################
# encoding: utf-8
from django.conf import settings
from django.contrib.auth import login, logout
from django.utils.importlib import import_module
from django.contrib.auth.models import AnonymousUser


class TestBrmedAuthenticationMiddleware(TestCase):
    def log_user(self, request, user):
        user.backend = 'src.authentication.backends.TokenAuthenticationBackend'
        request.user = user
        engine = import_module(settings.SESSION_ENGINE)
        request.session = engine.SessionStore()
        login(request, user)

        # Save the session values.
        request.session.save()

    def test_keep_logged_user_if_no_token_provided_and_has_not_expired(self):
        request = self.factory.get(self.__get_url())
        self.log_user(request, self.user)
        self.middleware.process_request(request)
        self.assertLoggedUser(request, self.user)

    def test_log_out_user_if_no_token_provided_but_it_has_expired(self):
        user = mommy.make_recipe('src.authentication.tests.expired_user')
        request = self.factory.get(self.__get_url())
        self.log_user(request, user)
        self.middleware.process_request(request)
        self.assertDidNotLoggedUser(request)

    def test_keep_logged_user_if_token_provided_is_the_same_and_has_not_expired(self):
        request = self.factory.get(self.__get_url(self.user.token))
        self.log_user(request, self.user)
        self.middleware.process_request(request)
        self.assertLoggedUser(request, self.user)

    def test_log_only_token_user_if_it_differs_from_session_user(self):
        new_user = mommy.make_recipe('src.authentication.tests.active_user')
        request = self.factory.get(self.__get_url(key=new_user.token))
        self.log_user(request, self.user)
        self.middleware.process_request(request)
        self.assertLoggedUser(request, new_user)

    def test_authentication_middleware_is_in_settings(self):
        self.assertIn('src.authentication.middleware.BrMedAuthenticationMiddleware', settings.MIDDLEWARE_CLASSES)

    def test_should_log_against_anonymous_user(self):
        request = self.factory.get(self.__get_url(self.user.token))
        self.log_user(request, self.user)
        logout(request)  # hack para criar a sessão
        request.user = AnonymousUser()
        self.middleware.process_request(request)
        self.assertLoggedUser(request, self.user)
"""
