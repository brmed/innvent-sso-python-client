# coding: utf-8
from datetime import datetime
from requests import Session

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def sso_hostname(path):
    if not hasattr(settings, 'SSO_HOST'):
        raise ImproperlyConfigured('You need to set the SSO_HOST in the settings.')

    return '{0}{1}'.format(settings.SSO_HOST, path)

def parse_datetime(dt_string):
    naive_dt_string = ' '.join(dt_string.split(' ')[0:-1])
    return datetime.strptime(naive_dt_string, '%Y-%m-%d %H:%M:%S')


class SSOAPIClient(object):

    def __init__(self):
        self._session = Session()
        self._session.auth = (
            settings.SSO_SERVICE_TOKEN, settings.SSO_SECRET_KEY
        )

    def retrieve_new_token(self):
        resp = self._session.get(sso_hostname('/access_token'))
        resp.raise_for_status()

        resp_dict = resp.json()
        resp_dict['expires_at'] = parse_datetime(resp_dict['expires_at'])
        return resp_dict

