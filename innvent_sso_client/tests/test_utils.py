# coding: utf-8
import unittest
from dateutil.parser import parse

from django.conf import settings

from .testtools import vcr
from ..utils import SSOAPIClient, sso_hostname


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
            exp_resp = SSOAPIClient()._get('/access_token', cookies={'session_id': '1234'})

        self.assertIn('token', resp_dict.keys())
        self.assertEqual(resp_dict['token'], exp_resp['token'])

        self.assertIn('expires_at', resp_dict.keys())
        expected_expires_at = parse(exp_resp['expires_at'], ignoretz=True)
        self.assertEqual(resp_dict['expires_at'], expected_expires_at)

    def test_create_user_should_return_the_user_id(self):
        with vcr.use_cassette('create_user_successful.json'):
            resp = SSOAPIClient().create_user(
                username='user',
                password='passwd',
                email='user@example.com',
                first_name='Test',
                last_name='User',
            )

        with vcr.use_cassette('create_user_successful.json'):
            post_data = {
                'login': 'user',
                'password': 'passwd',
                'email': 'user@example.com',
                'firstname': 'Test',
                'lastname': 'User'
            }

            exp_resp = SSOAPIClient()._post('/users', post_data)
            exp_dict = {'id': exp_resp['created_user_id']}

        self.assertEqual(exp_dict, resp)

    def test_get_user_should_return_the_user_correctly_by_username(self):
        with vcr.use_cassette('get_user_by_username_successful.json'):
            resp = SSOAPIClient().get_user('user')

        with vcr.use_cassette('get_user_by_username_successful.json'):
            exp_resp = SSOAPIClient()._get('/user_by_login', {'login': 'user'})
            exp_resp['username'] = exp_resp.pop('login')

        self.assertEqual(exp_resp, resp)

    def test_update_user_should_update_the_user_correctly_by_username(self):
        with vcr.use_cassette('update_user_by_username_successful.json'):
            update_resp = SSOAPIClient().update_user('user',
                first_name='User',
                last_name='Test',
            )

        self.assertTrue(update_resp)

        with vcr.use_cassette('get_user_after_update_successful.json'):
            get_user_resp = SSOAPIClient().get_user('user')

        self.assertEqual(get_user_resp['first_name'], 'User')
        self.assertEqual(get_user_resp['last_name'], 'Test')
