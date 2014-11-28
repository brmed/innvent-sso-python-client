# coding: utf-8

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'sqlite3.db',
    }
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
)

ROOT_URLCONF = 'django.contrib.auth.urls'
SECRET_KEY = 'this_is_not_required'
DEBUG = True
SSO_HOST = 'http://ssohost'
