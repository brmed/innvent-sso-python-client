# coding: utf-8
import base64
import json
from dateutil.parser import parse

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ImproperlyConfigured


class SSORequestFromSettingsMiddleware(object):

    def process_request(self, request):
        request.SSO_APPLICATION_SLUG = settings.SSO_APPLICATION_SLUG


class SSOMiddleware(object):

    def __init__(self, get_reponse):
        self.get_response = get_reponse

    def __call__(self, request):
        request.SSO_APPLICATION_SLUG = settings.SSO_APPLICATION_SLUG
        if not hasattr(request, 'user'):
            raise ImproperlyConfigured(
                "The SSOAuthenticationMiddleware required the authentication"
                " middleware to be installed. Edit your MIDDLEWARE_CLASSES"
                " settings to insert"
                " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
                " before the SSOAuthenticationMiddleware class."
            )

        if self.logout_expired_token_user(request):
            return self.get_response(request)

        try:
            session_token, token_expiration = self.get_session_data(request)
        except TypeError:
            return self.get_response(request)

        try:
            token, user_data = self.extract_user_data(request)
        except TypeError:
            return self.get_response(request)

        if token != session_token:
            return self.get_response(request)

        self.store_application_permission(request, user_data)

        user = authenticate(
            token=token,
            expiration_datetime=token_expiration,
            username=user_data['login'],
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
        )

        if not user:
            return self.get_response(request)

        if self.logout_expired_token_user(request, user):
            return self.get_response(request)

        request.user = user
        login(request, user)
        return self.get_response(request)

    def extract_user_data(self, request):
        b64_data = request.GET.get('data')
        if not b64_data:
            # não existe data na querystring
            return None

        json_data = base64.b64decode(b64_data)
        data = json.loads(json_data)

        return data['token'], data['user']

    def get_session_data(self, request):
        session_token = request.session.get('SSO_TOKEN')
        session_token_expiration = request.session.get('SSO_TOKEN_EXPIRATION')

        if not (session_token and session_token_expiration):
            # não existe token ou expiração na sessão
            return None

        token_expiration = parse(session_token_expiration, ignoretz=True)

        return session_token, token_expiration

    def logout_expired_token_user(self, request, user=None):
        user = user or request.user

        if user.is_authenticated:
            if not hasattr(user, 'ssousertoken'):
                return True

            if user.ssousertoken.has_expired:
                logout(request)
                return True

    def store_application_permission(self, request, user_data):
        applications = user_data['applications']
        curr_application = request.SSO_APPLICATION_SLUG

        permission = curr_application in applications or 'default' in applications

        request.session['SSO_APPLICATION_PERMISSION'] = permission