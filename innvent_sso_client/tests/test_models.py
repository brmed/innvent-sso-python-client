# coding:utf-8
from datetime import datetime, timedelta
from model_mommy import mommy

from django.test import TestCase
from django.db import IntegrityError
from django.contrib.auth import get_user_model

from ..models import SSOUserToken, DuplicatedTokenException


class SSOUserTokenTestCase(TestCase):

    def test_token_value_is_unique(self):
        mommy.make(SSOUserToken, token='123123')
        self.assertRaises(IntegrityError, mommy.make, SSOUserToken, token='123123')

    def test_user_is_unique(self):
        user_model = get_user_model()
        user = mommy.make(user_model)
        mommy.make(SSOUserToken, user=user)
        self.assertRaises(IntegrityError, mommy.make, SSOUserToken, user=user)

    def test_updates_last_modified_flag_on_change(self):
        sso_user_token = mommy.make(SSOUserToken)
        first_last_modified = sso_user_token.last_modified

        sso_user_token.token = 'xxxx'
        sso_user_token.save()

        self.assertNotEqual(first_last_modified, sso_user_token.last_modified)

    def test_checks_if_token_has_expired(self):
        #  expired token
        yesterday = datetime.now() - timedelta(days=1)
        sso_user_token = mommy.prepare(SSOUserToken, expiration_datetime=yesterday)
        self.assertTrue(sso_user_token.has_expired)
        #  valid token
        tomorrow = datetime.now() + timedelta(days=1)
        sso_user_token = mommy.prepare(SSOUserToken, expiration_datetime=tomorrow)
        self.assertFalse(sso_user_token.has_expired)

    def test_should_raise_duplicated_token_if_create_or_update_is_used_with_a_different_user(self):
        mommy.make(SSOUserToken, token='123123')

        user = mommy.make(get_user_model())

        self.assertRaises(
            DuplicatedTokenException,
            SSOUserToken.objects.create_or_update,
            user, '123123', datetime.now()
        )

    def test_should_not_raise_duplicated_token_if_create_or_update_is_used_with_same_user(self):
        user = mommy.make(get_user_model())

        mommy.make(SSOUserToken, token='123123', user=user)

        SSOUserToken.objects.create_or_update(user, '123123', datetime.now())
