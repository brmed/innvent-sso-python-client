# coding: utf-8
import json
from datetime import datetime
from dateutil.parser import parse
from mock import patch, Mock
from requests import Response, Session
from requests.exceptions import HTTPError

from django.conf import settings
from django.test import TestCase

from .testtools import vcr
from ..utils import SSOAPIClient, SSOPasswordPolicyError, sso_hostname, remove_data_from_url


def make_response(status_code, body=None, content=None):
    response = Response()
    response.status_code = status_code
    response.reason = 'Reason'
    response.url = sso_hostname('/users')
    response._content = content if content is not None else json.dumps(body).encode('utf-8')
    return response


PASSWORD_ERRORS_BODY = {
    'error': u'A senha precisa ter 8 caracteres. A senha já foi usada.',
    'password_errors': [
        {'rule': 'composition', 'message': u'A senha precisa ter 8 caracteres.'},
        {'rule': 'history', 'message': u'A senha já foi usada.'},
    ],
}


class SSOAPIClientTestCase(TestCase):

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

    @patch.object(SSOAPIClient, '_request')
    def test_retrieve_new_token_should_use_sso_session_id_settings(self, mocked_method):
        mocked_method.return_value = {'expires_at': datetime.now().isoformat()}

        session_id = 'dummy_session'

        with self.settings(SSO_SESSION_ID=session_id):
            SSOAPIClient().retrieve_new_token()

        call_args = ('get', '/access_token')
        call_kwargs = {'cookies': {'session_id': session_id}, 'params': None}

        mocked_method.assert_called_once_with(*call_args, **call_kwargs)

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

    def test_create_or_update_user_should_return_the_user_id(self):
        with vcr.use_cassette('create_or_update_user__create.json'):
            resp = SSOAPIClient().create_or_update_user(
                username='user',
                password='passwd',
                email='user@example.com',
                first_name='Test',
                last_name='User',
            )

        self.assertTrue(resp)

    def test_create_or_update_user_should_return_the_user_id(self):
        with vcr.use_cassette('create_or_update_user__update.json'):
            resp = SSOAPIClient().create_or_update_user(
                username='user',
                password='passwd',
                email='user@example.com',
                first_name='Test',
                last_name='User',
            )

        self.assertFalse(resp)

    def test_list_users_should_return_the_correct_dict(self):
        with vcr.use_cassette('list_users.json'):
            resp = SSOAPIClient().list_users()

        self.assertIn('total_pages', resp)
        self.assertIn('count', resp)

        self.assertIn('users', resp)
        self.assertIsInstance(resp['users'], list)

    def test_add_application_should_update_user_with_the_added_application(self):
        with vcr.use_cassette('add_application_to_user_success.json'):
            resp = SSOAPIClient().add_application_to_user('sudo', 'test-app')

        self.assertTrue(resp)

        with vcr.use_cassette('get_user_after_successful_application_addition.json'):
            user = SSOAPIClient().get_user('sudo')

        self.assertIn('applications', user)
        self.assertIn('test-app', user['applications'])

    def test_failed_add_application_should_not_update_user_with_the_added_application(self):
        with vcr.use_cassette('add_application_to_user_failure.json'):
            resp = SSOAPIClient().add_application_to_user('sudo', 'Must be slug')

        self.assertFalse(resp)

        with vcr.use_cassette('get_user_after_failed_application_addition.json'):
            user = SSOAPIClient().get_user('sudo')

        self.assertIn('applications', user)
        self.assertNotIn('Must be slug', user['applications'])

    def test_remove_application_should_update_user_with_the_removed_application(self):
        with vcr.use_cassette('remove_application_from_user_success.json'):
            resp = SSOAPIClient().remove_application_from_user('sudo', 'test-app')

        self.assertTrue(resp)

        with vcr.use_cassette('get_user_after_successful_application_remove.json'):
            user = SSOAPIClient().get_user('sudo')

        self.assertIn('applications', user)
        self.assertNotIn('test-app', user['applications'])

    def test_failed_remove_application_should_not_update_user_with_the_removed_application(self):
        with vcr.use_cassette('remove_application_from_user_failure.json'):
            resp = SSOAPIClient().remove_application_from_user('sudo', 'Must be slug')

        self.assertFalse(resp)

        with vcr.use_cassette('get_user_after_failed_application_remove.json'):
            user = SSOAPIClient().get_user('sudo')

        self.assertIn('applications', user)
        self.assertNotIn('test-app', user['applications'])

    def test_list_users_should_return_the_correct_dict(self):
        with vcr.use_cassette('list_applications.json'):
            resp = SSOAPIClient().list_applications()

        self.assertIsInstance(resp, list)
        self.assertIn('default', resp)


@patch.object(Session, 'request')
class SSOAPIClientPasswordPolicyTestCase(TestCase):

    def test_422_with_password_errors_raises_password_policy_error(self, mocked_request):
        mocked_request.return_value = make_response(422, PASSWORD_ERRORS_BODY)

        with self.assertRaises(SSOPasswordPolicyError) as context:
            SSOAPIClient()._put('/users/1', {'password': 'x'})

        error = context.exception
        self.assertEqual(PASSWORD_ERRORS_BODY['error'], error.message)
        self.assertEqual(PASSWORD_ERRORS_BODY['password_errors'], error.violations)
        self.assertEqual(['composition', 'history'], error.rules)
        self.assertEqual(422, error.response.status_code)
        self.assertEqual(PASSWORD_ERRORS_BODY['error'], unicode(error))
        self.assertEqual(PASSWORD_ERRORS_BODY['error'].encode('utf-8'), str(error))

    def test_password_policy_error_is_an_http_error(self, mocked_request):
        mocked_request.return_value = make_response(422, PASSWORD_ERRORS_BODY)

        self.assertRaises(HTTPError, SSOAPIClient()._put, '/users/1', {'password': 'x'})

    def test_422_without_password_errors_raises_http_error(self, mocked_request):
        mocked_request.return_value = make_response(422, {'error': 'invalid'})

        with self.assertRaises(HTTPError) as context:
            SSOAPIClient()._put('/users/1', {'login': 'x'})

        self.assertNotIsInstance(context.exception, SSOPasswordPolicyError)

    def test_422_without_json_body_raises_http_error(self, mocked_request):
        mocked_request.return_value = make_response(422, content=b'<html></html>')

        with self.assertRaises(HTTPError) as context:
            SSOAPIClient()._put('/users/1', {'login': 'x'})

        self.assertNotIsInstance(context.exception, SSOPasswordPolicyError)

    def test_other_errors_with_password_errors_raise_http_error(self, mocked_request):
        mocked_request.return_value = make_response(400, PASSWORD_ERRORS_BODY)

        with self.assertRaises(HTTPError) as context:
            SSOAPIClient()._put('/users/1', {'password': 'x'})

        self.assertNotIsInstance(context.exception, SSOPasswordPolicyError)

    def test_create_or_update_user_does_not_fallback_to_update_on_password_policy_error(self, mocked_request):
        mocked_request.return_value = make_response(422, PASSWORD_ERRORS_BODY)

        with patch.object(SSOAPIClient, 'update_user') as mocked_update:
            self.assertRaises(
                SSOPasswordPolicyError, SSOAPIClient().create_or_update_user,
                username='user', password='x', first_name='Test', last_name='User', email='u@example.com',
            )

        self.assertFalse(mocked_update.called)

    def test_create_or_update_user_still_falls_back_to_update_on_other_errors(self, mocked_request):
        mocked_request.return_value = make_response(409, {'error': 'already exists'})

        with patch.object(SSOAPIClient, 'update_user') as mocked_update:
            resp = SSOAPIClient().create_or_update_user(
                username='user', password='x', first_name='Test', last_name='User', email='u@example.com',
            )

        self.assertIsNone(resp)
        mocked_update.assert_called_once_with('user', password='x')

    def test_create_or_update_user_sends_only_the_password_when_updating(self, mocked_request):
        mocked_request.side_effect = [
            make_response(409, {'error': 'already exists'}),
            make_response(200, {'updated_user_id': '13'}),
        ]

        SSOAPIClient().create_or_update_user(
            username='user', password='x', first_name='Test', last_name='User', email='u@example.com',
        )

        self.assertEqual(2, mocked_request.call_count)
        self.assertEqual(
            (('post', sso_hostname('/users/user/')), {'data': {'password': 'x'}, 'params': None}),
            mocked_request.call_args_list[1]
        )


@patch.object(Session, 'request')
class SSOAPIClientChangeOwnPasswordTestCase(TestCase):

    def test_posts_passwords_in_the_body(self, mocked_request):
        mocked_request.return_value = make_response(200, {'updated_user_id': '13'})

        resp = SSOAPIClient().change_own_password('foo', 'current', 'new')

        self.assertTrue(resp)
        mocked_request.assert_called_once_with(
            'post', sso_hostname('/users/foo/password/'),
            data={'current_password': 'current', 'password': 'new'}, params=None,
        )

    def test_returns_false_when_nothing_was_updated(self, mocked_request):
        mocked_request.return_value = make_response(200, {'updated_user_id': '0'})

        self.assertFalse(SSOAPIClient().change_own_password('foo', 'current', 'new'))

    def test_wrong_current_password_raises_password_policy_error(self, mocked_request):
        mocked_request.return_value = make_response(422, {
            'error': u'Senha atual inválida.',
            'password_errors': [{'rule': 'current_password', 'message': u'Senha atual inválida.'}],
        })

        with self.assertRaises(SSOPasswordPolicyError) as context:
            SSOAPIClient().change_own_password('foo', 'wrong', 'new')

        self.assertEqual(['current_password'], context.exception.rules)

    def test_inactive_user_raises_password_policy_error(self, mocked_request):
        mocked_request.return_value = make_response(422, {
            'error': u'Usuário inativo.',
            'password_errors': [{'rule': 'inactive', 'message': u'Usuário inativo.'}],
        })

        with self.assertRaises(SSOPasswordPolicyError) as context:
            SSOAPIClient().change_own_password('foo', 'current', 'new')

        self.assertEqual(['inactive'], context.exception.rules)

    def test_user_not_found_raises_http_error(self, mocked_request):
        mocked_request.return_value = make_response(404, {'error': 'user not found'})

        with self.assertRaises(HTTPError) as context:
            SSOAPIClient().change_own_password('foo', 'current', 'new')

        self.assertNotIsInstance(context.exception, SSOPasswordPolicyError)
        self.assertEqual(404, context.exception.response.status_code)


@patch.object(SSOAPIClient, '_request')
class SSOAPIClientGetUsersByLastLoginTestCase(TestCase):

    def test_omits_less_than_when_false(self, mocked_request):
        SSOAPIClient().get_users_by_last_login('2026-01-01')

        mocked_request.assert_called_once_with('get', '/users/last_login/2026-01-01', params=None)

    def test_sends_less_than_when_true(self, mocked_request):
        SSOAPIClient().get_users_by_last_login('2026-01-01', less_than=True)

        mocked_request.assert_called_once_with(
            'get', '/users/last_login/2026-01-01', params={'less_than': True}
        )


class RemoveDataFromUrlTestCase(TestCase):

    def test_should_remove_data_query_param_from_url(self):
        expected_url = 'totally-a-url'
        url = '{0}?data=none'.format(expected_url)

        self.assertEqual(remove_data_from_url(url), expected_url)

    def test_should_not_remove_other_query_params_from_url(self):
        expected_url = 'totally-a-url?other=param'
        url = '{0}&data=none'.format(expected_url)

        self.assertEqual(remove_data_from_url(url), expected_url)

