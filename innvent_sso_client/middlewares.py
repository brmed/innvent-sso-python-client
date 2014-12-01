# coding: utf-8
from django.core.exceptions import ImproperlyConfigured


class SSOAuthenticationMiddleware(object):

    def process_request(self, request):

        if not hasattr(request, 'user'):
            raise ImproperlyConfigured(
                "The SSOAuthenticationMiddleware required the authentication"
                " middleware to be installed. Edit your MIDDLEWARE_CLASSES"
                " settings to insert"
                " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
                " before the SSOAuthenticationMiddleware class."
            )
