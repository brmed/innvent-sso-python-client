# coding: utf-8
from django.conf.global_settings import SESSION_ENGINE

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
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'innvent_sso_client.middlewares.SSOAuthenticationMiddleware',
)

ROOT_URLCONF = 'innvent_sso_client.tests.urls'
SECRET_KEY = 'this_is_not_required'
DEBUG = True

SSO_HOST = 'http://devsso:9292'
SSO_SERVICE_TOKEN = 'test_client_sso'
SSO_SECRET_KEY = '19a01733de77e077e16b3b4b25f40638fd66e3ef'

import django
if django.get_version().startswith('1.5'):
    TEST_RUNNER = 'discover_runner.DiscoverRunner'
    INSTALLED_APPS += ('discover_runner',)
