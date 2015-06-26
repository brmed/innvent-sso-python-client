# coding: utf-8
from django import template


register = template.Library()

def is_authenticated(request):
    authenticated = request.user.is_authenticated()
    app_permission =  request.session.get('SSO_APPLICATION_PERMISSION', True)

    return authenticated and app_permission

register.filter('is_authenticated', is_authenticated)
