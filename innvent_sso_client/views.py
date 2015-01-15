# coding: utf-8
from django.contrib.auth import logout as auth_logout
from django.http import HttpResponseRedirect

from .decorators import sso_required
from .utils import sso_hostname


@sso_required
def login(request):
    return HttpResponseRedirect('/')

@sso_required
def logout(request):
    auth_logout(request)
    qs = QueryDict(None, mutable=True)
    qs['callback_url'] = settings.SSO_LOGOUT_CALLBACK_URL

    logout_url = '{0}?{1}'.format(sso_hostname('/logout'), qs.urlencode(safe='/'))

    return HttpResponseRedirect(logout_url)
