# coding: utf-8
import urlparse
from datetime import datetime
from dateutil.parser import parse
from requests import Session
from requests.exceptions import HTTPError

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import QueryDict


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

    def _request(self, method, path, data=None, params=None, **kwargs):
        url = sso_hostname(path)

        resp = self._session.request(method, url, data=data, params=params, **kwargs)
        resp.raise_for_status()

        return resp.json()

    def _get(self, path, data=None, **kwargs):
        return self._request('get', path, params=data, **kwargs)

    def _post(self, path, data=None, **kwargs):
        return self._request('post', path, data, **kwargs)

    def retrieve_new_token(self):
        session_id = getattr(settings, 'SSO_SESSION_ID', '1234')
        resp = self._get('/access_token', cookies={'session_id': session_id})
        resp['expires_at'] = parse(resp['expires_at'], ignoretz=True)
        return resp

    def create_user(self, username, password, **user_kwargs):
        user_kwargs.update({'username': username, 'password': password})

        data = UserCompat.to_sso(user_kwargs)
        return {'id': self._post('/users', data)['created_user_id']}

    def get_user(self, username):
        resp = self._get('/user_by_login', data=json.dumps({'login': username}))
        return UserCompat.from_sso(resp)

    def update_user(self, username, **user_kwargs):
        user_data = self.get_user(username)

        user_data.update(user_kwargs)
        user_data = UserCompat.to_sso(user_data)

        resp = self._post('/users/{0}'.format(user_data['id']), user_data)
        return resp['updated_user_id'] != '0'

    def create_or_update_user(self, *args, **kwargs):
        try:
            self.create_user(*args, **kwargs)
            return True
        except HTTPError:
            self.update_user(*args, **kwargs)

    def create_invalid_user(self, usernames):
        return self._post('/create-invalid-users/', data={'logins': usernames})

    def list_users(self, username=None, page=1, limit=50):
        get_params = {'page': page, 'limit': limit}

        if username:
            get_params.update({'login': username})

        resp = self._get('/users/', data=get_params)

        return {
            'users': [UserCompat.from_sso(u) for u in resp['results']],
            'total_pages': resp['total_pages'],
            'count': resp['total_count'],
        }


class UserCompat(object):

    @classmethod
    def to_sso(cls, data):
        data['login'] = data.pop('username')
        data['firstname'] = data.pop('first_name')
        data['lastname'] = data.pop('last_name')

        return data

    @classmethod
    def from_sso(cls, data):
        data['username'] = data.pop('login')

        return data


def remove_data_from_url(url):
    scheme, netloc, path, query, fragment = urlparse.urlsplit(url)

    qs = QueryDict(query, mutable=True)
    qs.pop('data', None)
    query = qs.urlencode(safe='/')

    return urlparse.urlunsplit([scheme, netloc, path, query, fragment])
