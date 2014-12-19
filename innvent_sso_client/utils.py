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
        agent = 'python-requests/2.4.1 CPython/2.7.8 Linux/3.12.33-1-MANJARO'
        self._session.headers['User-Agent'] = agent

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
            'first_name': user_kwargs.get('first_name', ''),
            'last_name': user_kwargs.get('last_name', ''),
        }
        return {'id': self._post('/users', data)['created_user_id']}
