# coding: utf-8
from functools import wraps

from django.http import QueryDict, HttpResponseRedirect

from .utils import sso_hostname, SSOAPIClient


def sso_required(view_func):

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated():
            return view_func(request, *args, **kwargs)

        token_dict = SSOAPIClient().retrieve_new_token()

        qs = QueryDict(None, mutable=True)
        qs['callback_url'] = request.build_absolute_uri()
        qs['token'] = token_dict['token']

        redirect_url = '{0}?{1}'.format(
            sso_hostname('/login'), qs.urlencode(safe='/')
        )
        return HttpResponseRedirect(redirect_url)

    return _wrapped_view
