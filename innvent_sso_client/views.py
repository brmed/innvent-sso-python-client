# coding: utf-8
from django.conf import settings
from django.http import HttpResponseForbidden, HttpResponseRedirect, QueryDict

from .decorators import sso_required
from .utils import sso_hostname


@sso_required
def login(request):
    return HttpResponseRedirect('/')

def sso_logout(request):
    qs = QueryDict(None, mutable=True)
    qs['callback_url'] = request.build_absolute_uri(settings.SSO_LOGOUT_CALLBACK_PATH)

    logout_url = '{0}?{1}'.format(sso_hostname('/logout'), qs.urlencode(safe='/'))

    return HttpResponseRedirect(logout_url)

def forbidden(request):
    message = u'Esse usuário não tem permissão de acesso à essa aplicação.'
    return HttpResponseForbidden(message)
