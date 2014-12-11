# coding: utf-8
import base64
import json

from django.conf import settings
from django.contrib.auth import SESSION_KEY
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, RequestFactory
from django.utils.importlib import import_module

from ..middlewares import SSOMiddleware


class SSOMiddlewareTestCase(TestCase):

    def setUp(self):
        self.data = {
            'user': {
                'login': 'test',
                'email': 'test@example.com',
                'fist_name': 'Test',
                'last_name': 'User',
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

    def __build_session(self, request):
        engine = import_module(settings.SESSION_ENGINE)
        request.session = engine.SessionStore()
        request.session.save()

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
        self.__build_session(request)
        request.user = AnonymousUser()

        self.middleware.process_request(request)

        self.assertNotIn(SESSION_KEY, request.session)

