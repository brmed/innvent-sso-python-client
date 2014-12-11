# coding: utf-8
import base64
import json
from dateutil.parser import parse

from django.contrib.auth import authenticate, login
from django.core.exceptions import ImproperlyConfigured

from .backends import SSOBackend


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

        session_token = request.session.get('SSO_TOKEN')
        session_token_expiration = request.session.get('SSO_TOKEN_EXPIRATION')

        if not (session_token and session_token_expiration):
            # não existe token ou expiração na sessão
            return

        token, user_data = self.extract_user_data(request)

        if token != session_token:
            return

        token_expiration = parse(session_token_expiration)

        user = SSOBackend().authenticate(
            token=token,
            expiration_datetime=token_expiration,
            username=user_data['login'],
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
        )

        if user:
            request.user = user
            login(request, user)

    def extract_user_data(self, request):
        b64_data = request.GET.get('data')
        json_data = base64.b64decode(b64_data)
        data = json.loads(json_data)

        return data['token'], data['user']
