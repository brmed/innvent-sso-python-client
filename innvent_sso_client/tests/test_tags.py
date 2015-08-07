# coding: utf-8
from mock import patch, Mock

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.test.utils import override_settings

from .testtools import TestCase
from ..templatetags.sso_tags import is_authenticated


class IsAuthenticatedFilterTestCase(TestCase):

    def setUp(self):
        self.request = RequestFactory().get('/')
        self.request.user = AnonymousUser()

        self._build_session(self.request)

    @patch.object(AnonymousUser, 'is_authenticated', Mock(return_value=False))
    def test_should_return_false_if_user_is_not_authenticated(self):
        self.assertFalse(is_authenticated(self.request))

    @patch.object(AnonymousUser, 'is_authenticated', Mock(return_value=True))
    def test_should_return_false_if_SSO_APPLICATION_PERMISSION_is_false(self):
        self.request.session['SSO_APPLICATION_PERMISSION'] = False
        self.assertFalse(is_authenticated(self.request))

    @patch.object(AnonymousUser, 'is_authenticated', Mock(return_value=True))
    def test_should_return_true_only_if_both_SSO_APPLICATION_PERMISSION_and_user_is_authenticated(self):
        self.request.session['SSO_APPLICATION_PERMISSION'] = True
        self.assertTrue(is_authenticated(self.request))

    @patch.object(AnonymousUser, 'is_authenticated', Mock(return_value=True))
    @override_settings(SSO_CHECK_APPLICATION_PERMISSION = False)
    def test_should_return_true_if_user_is_authenticated_and_does_not_need_to_check_for_app_permission(self):
        self.request.session['SSO_APPLICATION_PERMISSION'] = False
        self.assertTrue(is_authenticated(self.request))
