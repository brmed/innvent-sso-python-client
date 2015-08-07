# coding: utf-8
from django import template
from django.conf import settings


register = template.Library()


def is_authenticated(request):
    authenticated = hasattr(request, 'user') and request.user.is_authenticated()
    app_permission = True

    check_application_permission = getattr(
        settings, 'SSO_CHECK_APPLICATION_PERMISSION', True
    )

    if check_application_permission:
        app_permission = request.session.get('SSO_APPLICATION_PERMISSION', True)

    return authenticated and app_permission

register.filter('is_authenticated', is_authenticated)
