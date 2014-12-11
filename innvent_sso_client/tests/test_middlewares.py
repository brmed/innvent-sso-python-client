# coding: utf-8

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, RequestFactory

from ..middlewares import SSOMiddleware


class SSOMiddlewareTestCase(TestCase):

    def setUp(self):
        self.url = "http://testserver/sso-required/?data=eyJ1c2VyIjp7ImxvZ2luIjoidGVzdCIsImVtYWlsIjoidGVzdEBleGFtcGxl%0ALmNvbSIsImZpcnN0X25hbWUiOiJUZXN0IiwibGFzdF9uYW1lIjoiVXNlciJ9%0ALCJ0b2tlbiI6ImIwYWQ1ZTMwNWFhOGExMGViZTk1NTUyMGI1YmFiOTA3In0%3D%0A"

        self.factory = RequestFactory()
        self.middleware = SSOMiddleware()

    def test_middleware_requires_authentication_middleware(self):
        request = self.factory.get(self.url)

        self.assertRaises(
            ImproperlyConfigured, self.middleware.process_request, request
        )


