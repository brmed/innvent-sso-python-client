# coding: utf-8

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

ROOT_URLCONF = 'django.contrib.auth.urls'
SECRET_KEY = 'this_is_not_required'
DEBUG = True
SSO_HOST = 'http://ssohost'

import django
if django.get_version().startswith('1.5'):
    TEST_RUNNER = 'discover_runner.DiscoverRunner'
    INSTALLED_APPS += ('discover_runner',)
