# coding: utf-8
import unittest

from django.conf import settings

from ..utils import SSOAPIClient


class SSOAPIClientTestCase(unittest.TestCase):

    def test_sso_client_must_have_a_correct_session_attached_to_it(self):
        client = SSOAPIClient()


        expected_auth = (settings.SSO_SERVICE_TOKEN, settings.SSO_SECRET_KEY)

        self.assertTrue(hasattr(client, '_session'))
        self.assertEqual(client._session.auth, expected_auth)

