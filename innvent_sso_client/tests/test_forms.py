# coding: utf-8
from mock import patch, Mock
from model_mommy import mommy
from requests import Session
from requests.exceptions import HTTPError

from django.contrib.auth import get_user_model
from django.test import TestCase

from ..utils import SSOAPIClient, SSOPasswordPolicyError, sso_hostname
from ..forms import (
    SSOUserCreationForm, SSOUserChangeForm, SSOSetPasswordForm, SSOPasswordChangeForm, SSORecoverPasswordForm
)


def password_policy_error(*violations):
    message = u' '.join(violation['message'] for violation in violations)
    return SSOPasswordPolicyError(message, list(violations))


COMPOSITION = {'rule': 'composition', 'message': u'A senha precisa ter 8 caracteres.'}
FORBIDDEN_WORD = {'rule': 'forbidden_word', 'message': u'A senha não pode conter o login.'}
HISTORY = {'rule': 'history', 'message': u'A senha já foi usada.'}
CURRENT_PASSWORD = {'rule': 'current_password', 'message': u'Senha atual inválida.'}
INACTIVE = {'rule': 'inactive', 'message': u'Usuário inativo.'}
REQUIRED = {'rule': 'required', 'message': u'Informe a nova senha.'}
UNKNOWN = {'rule': 'new_rule', 'message': u'Regra nova.'}


class SSOUserCreationFormTestCase(TestCase):

    def setUp(self):
        self.data = {
            'username': 'foo',
            'password1': 'bar',
            'password2': 'bar',
        }

    @patch.object(SSOAPIClient, 'create_or_update_user')
    def test_calls_sso_api_client_correctly(self, mocked_api_call):
        form = SSOUserCreationForm(self.data)
        self.assertTrue(form.is_valid())
        form.save()

        call_kwargs = {
            'username': 'foo',
            'password': 'bar',
            'first_name': '',
            'last_name': '',
            'email': '',
        }
        mocked_api_call.assert_called_once_with(**call_kwargs)

    @patch.object(SSOAPIClient, 'create_or_update_user')
    def test_password_policy_error_becomes_error_on_password1(self, mocked_api_call):
        mocked_api_call.side_effect = password_policy_error(COMPOSITION, HISTORY)

        form = SSOUserCreationForm(self.data)

        self.assertFalse(form.is_valid())
        self.assertEqual([COMPOSITION['message'], HISTORY['message']], form.errors['password1'])
        self.assertNotIn('password2', form.errors)
        self.assertEqual(0, get_user_model().objects.count())

    @patch.object(SSOAPIClient, 'create_or_update_user')
    def test_does_not_call_sso_when_passwords_do_not_match(self, mocked_api_call):
        self.data['password2'] = 'other'

        form = SSOUserCreationForm(self.data)

        self.assertFalse(form.is_valid())
        self.assertFalse(mocked_api_call.called)


class SSOUserChangeFormTestCase(TestCase):

    @patch.object(SSOAPIClient, 'update_user_by_id')
    @patch.object(SSOAPIClient, 'check_user_identity')
    @patch.object(SSOAPIClient, 'get_user')
    def test_calls_sso_api_client_correctly(self, mocked_get_user, mocked_check_user_identity, mocked_api_call):
        user = mommy.make(get_user_model(), username='foo')
        mocked_get_user.return_value = {'id': user.id}
        mocked_check_user_identity.return_value = True
        form = SSOUserChangeForm(instance=user)
        data = form.initial.copy()
        data.update({
            'first_name': 'name',
            'last_name': 'last_name',
            'email': 'email@email.com',
            'is_active': True
        })

        form = SSOUserChangeForm(data, instance=user)
        self.assertTrue(form.is_valid())
        form.save()

        call_kwargs = {
            'login': 'foo',
            'firstname': 'name',
            'lastname': 'last_name',
            'email': 'email@email.com',
            'is_active': True
        }
        mocked_api_call.assert_called_once_with(1, **call_kwargs)


class SSOSetPasswordFormTestcase(TestCase):

    def setUp(self):
        self.user = mommy.make(get_user_model())
        self.user.set_password('old')
        self.user.save()
        self.data = {'new_password1': 'foo', 'new_password2': 'foo'}

    @patch.object(SSOAPIClient, 'update_user_by_id')
    @patch.object(SSOAPIClient, 'check_user_identity')
    @patch.object(SSOAPIClient, 'get_user')
    def test_calls_sso_api_client_correctly(self, mocked_get_user, mocked_check_user_identity, mocked_api_call):
        mocked_get_user.return_value = {'id': self.user.id}
        mocked_check_user_identity.return_value = True

        form = SSOSetPasswordForm(self.user, self.data)
        self.assertTrue(form.is_valid())
        form.save()

        mocked_api_call.assert_called_once_with(self.user.id, password='foo')
        self.assertTrue(get_user_model().objects.get(pk=self.user.pk).check_password('foo'))

    @patch.object(Session, 'request')
    @patch.object(SSOAPIClient, 'get_user', Mock(return_value={'id': 7}))
    def test_sends_only_the_password_to_the_sso(self, mocked_request):
        mocked_request.return_value = Mock(status_code=200, json=Mock(return_value={'updated_user_id': '7'}))
        self.user.email = 'local@example.com'
        self.user.first_name = 'Local'
        self.user.last_name = 'Name'

        form = SSOSetPasswordForm(self.user, self.data)

        self.assertTrue(form.is_valid())
        mocked_request.assert_called_once_with(
            'put', sso_hostname('/users/7'), data={'password': 'foo'}, params=None
        )

    @patch.object(SSOAPIClient, 'update_user_by_id')
    @patch.object(SSOAPIClient, 'get_user', Mock(return_value={'id': 7}))
    def test_password_policy_error_becomes_error_on_new_password1(self, mocked_api_call):
        mocked_api_call.side_effect = password_policy_error(COMPOSITION, FORBIDDEN_WORD, HISTORY)

        form = SSOSetPasswordForm(self.user, self.data)

        self.assertFalse(form.is_valid())
        self.assertEqual(
            [COMPOSITION['message'], FORBIDDEN_WORD['message'], HISTORY['message']],
            form.errors['new_password1']
        )
        self.assertNotIn('new_password1', form.cleaned_data)
        self.assertNotIn('new_password2', form.errors)
        self.assertTrue(get_user_model().objects.get(pk=self.user.pk).check_password('old'))

    @patch.object(SSOAPIClient, 'update_user_by_id')
    @patch.object(SSOAPIClient, 'get_user', Mock(return_value={'id': 7}))
    def test_password_policy_error_without_violations_uses_error_message(self, mocked_api_call):
        mocked_api_call.side_effect = SSOPasswordPolicyError(u'Senha recusada.', [])

        form = SSOSetPasswordForm(self.user, self.data)

        self.assertFalse(form.is_valid())
        self.assertEqual([u'Senha recusada.'], form.errors['new_password1'])

    @patch.object(SSOAPIClient, 'update_user_by_id')
    @patch.object(SSOAPIClient, 'get_user', Mock(return_value={'id': 7}))
    def test_other_http_errors_are_not_converted(self, mocked_api_call):
        mocked_api_call.side_effect = HTTPError('500 Server Error')

        form = SSOSetPasswordForm(self.user, self.data)

        self.assertRaises(HTTPError, form.is_valid)

    @patch.object(SSOAPIClient, 'update_user_by_id')
    @patch.object(SSOAPIClient, 'get_user')
    def test_does_not_call_sso_when_passwords_do_not_match(self, mocked_get_user, mocked_api_call):
        self.data['new_password2'] = 'other'

        form = SSOSetPasswordForm(self.user, self.data)

        self.assertFalse(form.is_valid())
        self.assertIn('new_password2', form.errors)
        self.assertNotIn('new_password1', form.errors)
        self.assertFalse(mocked_get_user.called)
        self.assertFalse(mocked_api_call.called)


class SSOPasswordChangeFormTestcase(TestCase):

    def setUp(self):
        self.user = mommy.make(get_user_model())
        self.user.set_password('local')
        self.user.save()
        self.data = {'new_password1': 'foo', 'new_password2': 'foo', 'old_password': 'old'}

    @patch.object(SSOAPIClient, 'update_user_by_id')
    @patch.object(SSOAPIClient, 'check_user_identity')
    @patch.object(SSOAPIClient, 'change_own_password')
    def test_changes_own_password_on_sso_once(self, mocked_change, mocked_check_user_identity, mocked_update):
        form = SSOPasswordChangeForm(self.user, self.data)

        self.assertTrue(form.is_valid())
        form.save()

        mocked_change.assert_called_once_with(self.user.username, 'old', 'foo')
        self.assertFalse(mocked_check_user_identity.called)
        self.assertFalse(mocked_update.called)

    @patch.object(SSOAPIClient, 'change_own_password')
    def test_save_updates_only_the_local_password(self, mocked_change):
        form = SSOPasswordChangeForm(self.user, self.data)
        self.assertTrue(form.is_valid())

        form.save()

        self.assertEqual(1, mocked_change.call_count)
        self.assertTrue(get_user_model().objects.get(pk=self.user.pk).check_password('foo'))

    @patch.object(SSOAPIClient, 'change_own_password', Mock())
    def test_does_not_check_old_password_against_local_password(self):
        form = SSOPasswordChangeForm(self.user, self.data)

        self.assertTrue(form.is_valid())

    @patch.object(SSOAPIClient, 'change_own_password', Mock())
    def test_accepts_new_password_equal_to_old_password(self):
        self.data['old_password'] = 'foo'

        form = SSOPasswordChangeForm(self.user, self.data)

        self.assertTrue(form.is_valid())

    @patch.object(SSOAPIClient, 'change_own_password')
    def test_current_password_rule_becomes_error_on_old_password(self, mocked_change):
        mocked_change.side_effect = password_policy_error(CURRENT_PASSWORD)

        form = SSOPasswordChangeForm(self.user, self.data)

        self.assertFalse(form.is_valid())
        self.assertEqual([CURRENT_PASSWORD['message']], form.errors['old_password'])
        self.assertNotIn('new_password1', form.errors)
        self.assertNotIn('new_password2', form.errors)
        self.assertTrue(get_user_model().objects.get(pk=self.user.pk).check_password('local'))

    @patch.object(SSOAPIClient, 'change_own_password')
    def test_policy_rules_become_errors_on_new_password1(self, mocked_change):
        mocked_change.side_effect = password_policy_error(COMPOSITION, FORBIDDEN_WORD, HISTORY)

        form = SSOPasswordChangeForm(self.user, self.data)

        self.assertFalse(form.is_valid())
        self.assertEqual(
            [COMPOSITION['message'], FORBIDDEN_WORD['message'], HISTORY['message']],
            form.errors['new_password1']
        )
        self.assertNotIn('old_password', form.errors)

    @patch.object(SSOAPIClient, 'change_own_password')
    def test_inactive_rule_becomes_error_on_new_password1(self, mocked_change):
        mocked_change.side_effect = password_policy_error(INACTIVE)

        form = SSOPasswordChangeForm(self.user, self.data)

        self.assertFalse(form.is_valid())
        self.assertEqual([INACTIVE['message']], form.errors['new_password1'])

    @patch.object(SSOAPIClient, 'change_own_password')
    def test_required_and_unknown_rules_become_errors_on_new_password1(self, mocked_change):
        mocked_change.side_effect = password_policy_error(REQUIRED, UNKNOWN)

        form = SSOPasswordChangeForm(self.user, self.data)

        self.assertFalse(form.is_valid())
        self.assertEqual([REQUIRED['message'], UNKNOWN['message']], form.errors['new_password1'])
        self.assertNotIn('new_password2', form.errors)
        self.assertNotIn('old_password', form.errors)

    def test_old_password_is_labeled_as_current_password(self):
        form = SSOPasswordChangeForm(self.user)

        self.assertEqual(u'Senha atual', form.fields['old_password'].label)
        self.assertEqual(['old_password', 'new_password1', 'new_password2'], list(form.fields))

    @patch.object(SSOAPIClient, 'change_own_password')
    def test_does_not_call_sso_when_passwords_do_not_match(self, mocked_change):
        self.data['new_password2'] = 'other'

        form = SSOPasswordChangeForm(self.user, self.data)

        self.assertFalse(form.is_valid())
        self.assertFalse(mocked_change.called)
        self.assertIn('new_password2', form.errors)
        self.assertNotIn('new_password1', form.errors)

    @patch.object(SSOAPIClient, 'change_own_password')
    def test_does_not_call_sso_without_old_password(self, mocked_change):
        del self.data['old_password']

        form = SSOPasswordChangeForm(self.user, self.data)

        self.assertFalse(form.is_valid())
        self.assertFalse(mocked_change.called)

    @patch.object(SSOAPIClient, 'change_own_password')
    def test_user_not_found_is_not_converted(self, mocked_change):
        mocked_change.side_effect = HTTPError('404 Client Error: Not Found')

        form = SSOPasswordChangeForm(self.user, self.data)

        self.assertRaises(HTTPError, form.is_valid)


class SSORecoverPasswordFormTestcase(TestCase):

    def setUp(self):
        self.user = mommy.make(get_user_model())
        self.data = {'new_password1': 'foo', 'new_password2': 'foo'}

    @patch.object(SSOAPIClient, 'update_user_by_id')
    @patch.object(SSOAPIClient, 'check_user_identity', Mock(return_value=False))
    @patch.object(SSOAPIClient, 'get_user', Mock(return_value={'id': 7}))
    def test_updates_password_on_sso(self, mocked_update):
        form = SSORecoverPasswordForm(self.user, self.data)

        self.assertTrue(form.is_valid())
        form.save()

        mocked_update.assert_called_once_with(7, password='foo')
        self.assertTrue(get_user_model().objects.get(pk=self.user.pk).check_password('foo'))

    @patch.object(SSOAPIClient, 'update_user_by_id')
    @patch.object(SSOAPIClient, 'check_user_identity', Mock(return_value=True))
    @patch.object(SSOAPIClient, 'get_user', Mock(return_value={'id': 7}))
    def test_rejects_current_password_without_updating_sso(self, mocked_update):
        form = SSORecoverPasswordForm(self.user, self.data)

        self.assertFalse(form.is_valid())
        self.assertIn(u'Você não pode utilizar uma senha que já utilizou antes.', form.non_field_errors())
        self.assertFalse(mocked_update.called)

    @patch.object(SSOAPIClient, 'update_user_by_id')
    @patch.object(SSOAPIClient, 'check_user_identity', Mock(return_value=False))
    @patch.object(SSOAPIClient, 'get_user', Mock(return_value={'id': 7}))
    def test_password_policy_error_becomes_error_on_new_password1(self, mocked_update):
        mocked_update.side_effect = password_policy_error(HISTORY)

        form = SSORecoverPasswordForm(self.user, self.data)

        self.assertFalse(form.is_valid())
        self.assertEqual([HISTORY['message']], form.errors['new_password1'])
