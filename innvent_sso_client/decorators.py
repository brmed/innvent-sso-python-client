# coding: utf-8
from django.contrib.auth.decorators import login_required

from .utils import sso_hostname


def sso_required(*args, **kwargs):
    kwargs['login_url'] = sso_hostname('/login/')
    kwargs['redirect_field_name'] = 'callback_url'
    return login_required(*args, **kwargs)
