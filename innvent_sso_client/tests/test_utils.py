# coding: utf-8
import os
import unittest
from vcr import VCR

from django.conf import settings

from ..utils import SSOAPIClient, sso_hostname, parse_datetime

vcr = VCR(
    serializer = 'json',
    cassette_library_dir = os.path.join(os.path.dirname(__file__), os.path.pardir, 'cassettes'),
    record_mode = 'once',
    match_on = ['method', 'uri', 'port', 'headers', 'body']
)


class SSOAPIClientTestCase(unittest.TestCase):

    def test_sso_client_must_have_a_correct_session_attached_to_it(self):
        client = SSOAPIClient()

        expected_auth = (settings.SSO_SERVICE_TOKEN, settings.SSO_SECRET_KEY)

        self.assertTrue(hasattr(client, '_session'))
        self.assertEqual(client._session.auth, expected_auth)

    def test_retrieve_new_token_should_return_correctly(self):
        with vcr.use_cassette('access_token_valid.json'):
            resp_dict = SSOAPIClient().retrieve_new_token()

        with vcr.use_cassette('access_token_valid.json'):
            exp_resp = SSOAPIClient()._session.get(sso_hostname('/access_token'))
            expected_dict = exp_resp.json()

        self.assertIn('token', resp_dict.keys())
        self.assertEqual(resp_dict['token'], expected_dict['token'])

        self.assertIn('expires_at', resp_dict.keys())
        expected_expires_at = parse_datetime(expected_dict['expires_at'])
        self.assertEqual(resp_dict['expires_at'], expected_expires_at)

