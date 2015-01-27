#coding: utf-8
from model_mommy import mommy

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.timezone import datetime, timedelta

from ..backends import SSOBackend
from ..models import SSOUserToken


class SSOBackendTestCase(TestCase):

    def setUp(self):
        self.UserModel = get_user_model()
        self.expiration_datetime = datetime.now() + timedelta(days=1)
        self.backend_kwargs = {
            u'username': u'foo',
            u'email': u'foo@foo.com',
            u'first_name': u'foo',
            u'last_name': u'bar',
            u'token': u'123123',
            u'expiration_datetime': self.expiration_datetime,
        }
        self.backend = SSOBackend()

    def test_sso_backends_inherits_django_model_backend(self):
        from django.contrib.auth.backends import ModelBackend
        ModelBackend.authenticate
        self.assertIsInstance(self.backend, ModelBackend)

    def test_creates_sso_user_and_user_if_none_exists(self):
        self.assertEqual(0, SSOUserToken.objects.count())
        self.assertEqual(0, self.UserModel.objects.count())

        user = self.backend.authenticate(**self.backend_kwargs)
        self.assertEqual(1, SSOUserToken.objects.count())
        self.assertEqual(1, self.UserModel.objects.count())

        self.assertEqual(self.backend_kwargs['username'], user.username)
        self.assertEqual(self.backend_kwargs['email'], user.email)
        self.assertEqual(self.backend_kwargs['first_name'], user.first_name)
        self.assertEqual(self.backend_kwargs['last_name'], user.last_name)

        self.assertEqual(self.backend_kwargs['token'], user.ssousertoken.token)
        self.assertEqual(self.backend_kwargs['expiration_datetime'], user.ssousertoken.expiration_datetime)

    def test_recovers_user_if_it_already_exists(self):
        created_user = mommy.make(self.UserModel, username=self.backend_kwargs['username'])

        user = self.backend.authenticate(**self.backend_kwargs)

        self.assertEqual(user, created_user)

    def test_updates_sso_user_token_if_it_already_exists(self):
        created_user = mommy.make(self.UserModel, username=self.backend_kwargs['username'])
        created_token = mommy.make(SSOUserToken, user=created_user)

        user = self.backend.authenticate(**self.backend_kwargs)

        self.assertEqual(1, SSOUserToken.objects.count())
        self.assertNotEqual(created_token.token, user.ssousertoken.token)

    def test_should_return_none_if_no_token_or_expiration_is_present(self):
        user = self.backend.authenticate(username='foo')

        self.assertEqual(user, None)

    def test_should_return_none_if_token_is_present_with_a_different_user(self):
        created_user = mommy.make(self.UserModel)
        created_token = mommy.make(SSOUserToken, token=self.backend_kwargs['token'], user=created_user)

        user = self.backend.authenticate(**self.backend_kwargs)

        self.assertIsNone(user)

    def test_updates_sso_user_token_if_it_already_exists_and_has_the_same_key(self):
        created_user = mommy.make(self.UserModel, username=self.backend_kwargs['username'])
        created_token = mommy.make(SSOUserToken, token=self.backend_kwargs['token'], user=created_user)

        user = self.backend.authenticate(**self.backend_kwargs)

        self.assertEqual(1, SSOUserToken.objects.count())
        self.assertEqual(created_token.token, user.ssousertoken.token)

