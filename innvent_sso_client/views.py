# coding: utf-8
from django.conf import settings
from django.http import HttpResponseForbidden, HttpResponseRedirect, QueryDict

from .decorators import sso_required
from .utils import sso_hostname

import re


@sso_required
def login(request):
    return HttpResponseRedirect('/')

def sso_logout(request):
    qs = QueryDict(None, mutable=True)
    qs['callback_url'] = '{}?redirect_url={}'.format(request.build_absolute_uri(settings.SSO_LOGOUT_CALLBACK_PATH), re.sub(r'^https?://[^/]+/', '/', request.META.get('HTTP_REFERER', '/')))

    logout_url = '{0}?{1}'.format(sso_hostname('/logout'), qs.urlencode(safe='/'))

    return HttpResponseRedirect(logout_url)

def forbidden(request):
    message = u'Esse usuário não tem permissão de acesso a essa aplicação.'
    return HttpResponseForbidden(message)
