# coding: utf-8
from django.conf.global_settings import SESSION_ENGINE, AUTHENTICATION_BACKENDS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/tmp/sqlite3.db',
        'TEST_NAME': ':memory:',
    }
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'innvent_sso_client',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

AUTHENTICATION_BACKENDS += ('innvent_sso_client.backends.SSOBackend',)

ROOT_URLCONF = 'innvent_sso_client.tests.urls'
SECRET_KEY = 'this_is_not_required'
DEBUG = True

SSO_HOST = 'http://devsso:9292'
SSO_SERVICE_TOKEN = 'test_client_sso'
SSO_SECRET_KEY = '28e1ea815e74c31379b718e8d70000f93b928bd5'

import django
if django.get_version().startswith('1.5'):
    TEST_RUNNER = 'discover_runner.DiscoverRunner'
    INSTALLED_APPS += ('discover_runner',)
