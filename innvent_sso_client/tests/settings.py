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
SSO_SERVICE_TOKEN = 'sso_dev'
SSO_SECRET_KEY = '8370e1fd0486968d3adf9cd9e48f25fb0873dec6'

import django
if django.get_version().startswith('1.5'):
    TEST_RUNNER = 'discover_runner.DiscoverRunner'
    INSTALLED_APPS += ('discover_runner',)
