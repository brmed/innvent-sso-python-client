# coding: utf-8
import unittest
from mock import patch, Mock

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse, QueryDict
from django.test import RequestFactory
from django.test.utils import override_settings

from ..decorators import sso_required
from ..utils import sso_hostname


@sso_required
def view(request):
    return HttpResponse('OK')


class SSORequiredTestCase(unittest.TestCase):

    def setUp(self):
        factory = RequestFactory()
        self.url = '/foo/bar/'
        self.request = factory.get(self.url)

    def test_should_redirect_to_login_path_of_settings_sso_host(self):
        qs = QueryDict(None, mutable=True)
        qs['callback_url'] = 'http://testserver{0}'.format(self.url)
        expected_url = '{0}?{1}'.format(
            sso_hostname('/login/'), qs.urlencode(safe='/')
        )

        self.request.user = AnonymousUser()
        response = view(self.request)

        self.assertEqual(302, response.status_code)
        self.assertEqual(expected_url, response['Location'])

    @patch.object(AnonymousUser, 'is_authenticated', Mock(return_value=True))
    def test_should_not_redirect_for_logged_user(self):
        self.request.user = AnonymousUser()
        response = view(self.request)

        self.assertTrue(self.request.user.is_authenticated)
        self.assertEqual(200, response.status_code)
        self.assertEqual('OK', response.content)
