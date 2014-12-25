# coding: utf-8
from datetime import datetime
from dateutil.parser import parse
from requests import Session

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def sso_hostname(path):
    if not hasattr(settings, 'SSO_HOST'):
        raise ImproperlyConfigured('You need to set the SSO_HOST in the settings.')

    return '{0}{1}'.format(settings.SSO_HOST, path)


class SSOAPIClient(object):

    def __init__(self):
        self._session = Session()
        self._session.auth = (
            settings.SSO_SERVICE_TOKEN, settings.SSO_SECRET_KEY
        )
        self._session.headers['User-Agent'] = 'Innvent SSO Python Client'

    def _request(self, method, path, data=None, **kwargs):
        url = sso_hostname(path)

        resp = self._session.request(method, url, data=data, **kwargs)
        resp.raise_for_status()

        return resp.json()

    def _get(self, path, data=None, **kwargs):
        return self._request('get', path, data, **kwargs)

    def _post(self, path, data=None, **kwargs):
        return self._request('post', path, data, **kwargs)

    def retrieve_new_token(self):
        resp = self._get('/access_token')
        resp['expires_at'] = parse(resp['expires_at'], ignoretz=True)
        return resp

    def create_user(self, username, passwd, **user_kwargs):
        data = {
            'login': username,
            'password': passwd,
            'email': user_kwargs.get('email', ''),
            'firstname': user_kwargs.get('first_name', ''),
            'lastname': user_kwargs.get('last_name', ''),
        }
        return {'id': self._post('/users', data)['created_user_id']}

    def get_user(self, username):
        resp = self._get('/user_by_login', data={'login': username})
        resp['username'] = resp.pop('login')
        return resp

    def update_user(self, username, **user_kwargs):
        user_id = self.get_user(username)['id']

        resp = self._post('/users/{0}'.format(user_id), user_kwargs)
