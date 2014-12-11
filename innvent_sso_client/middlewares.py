# coding: utf-8
import base64
import json

from django.core.exceptions import ImproperlyConfigured


class SSOMiddleware(object):

    def process_request(self, request):

        if not hasattr(request, 'user'):
            raise ImproperlyConfigured(
                "The SSOAuthenticationMiddleware required the authentication"
                " middleware to be installed. Edit your MIDDLEWARE_CLASSES"
                " settings to insert"
                " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
                " before the SSOAuthenticationMiddleware class."
            )

        if not ('SSO_TOKEN' in request.session and 'SSO_TOKEN_EXPIRATION' in request.session):
            # não existe token ou expiração na sessão
            return


    def extract_user_data(self, request):
        b64_data = request.GET.get('data')
        json_data = base64.b64decode(b64_data)
        data = json.loads(json_data)

        return data['token'], data['user']
