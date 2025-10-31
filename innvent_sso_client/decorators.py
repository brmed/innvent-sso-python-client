# coding: utf-8
from functools import wraps
from Cookie import SimpleCookie

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import QueryDict, HttpResponseRedirect, HttpResponseForbidden

from .utils import sso_hostname, SSOAPIClient, remove_data_from_url


def sso_required(view_func):

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        redirect_path = request.GET.get('RedirectPath', None)
        source_redirect = 'brnet'

        if request.user.is_authenticated():
            check_application_permission = getattr(settings, 'SSO_CHECK_APPLICATION_PERMISSION', True)
            application_permission = request.session.get('SSO_APPLICATION_PERMISSION', True)

            if not check_application_permission or application_permission or request.GET.get('source_redirect') == 'knowledge_base' or redirect_path:
                return view_func(request, *args, **kwargs)
            else:
                forbidden_url = reverse('forbidden_application')
                return HttpResponseRedirect(forbidden_url)

        token_dict = SSOAPIClient().retrieve_new_token()

        callback = request.build_absolute_uri(getattr(settings, 'SSO_CALLBACK_PATH', None))
        callback_url = remove_data_from_url(callback)

        if redirect_path:
            source_redirect = 'knowledge_base'
        else:
            redirect_path = request.path if request.path != '/' else ''

        qs = QueryDict(None, mutable=True)
        qs['callback_url'] = callback_url
        qs['source_redirect'] = source_redirect
        qs['redirect_url'] = redirect_path
        qs['token'] = token_dict['token']

        if request.COOKIES.get('display_custom_logo'):
            qs['interface'] = request.COOKIES.get('logo_key')

        redirect_url = '{0}?{1}'.format(
            sso_hostname('/authorize'), qs.urlencode(safe='/')
        )

        request.session["SSO_TOKEN"] = token_dict['token']
        request.session["SSO_TOKEN_EXPIRATION"] = token_dict['expires_at'].isoformat()

        if 'HTTP_COOKIE' in request.META:
            cookie = SimpleCookie(request.META.get('HTTP_COOKIE', '') or '')
            if 'display_custom_logo' in cookie:
                del cookie['display_custom_logo']
            if 'logo_key' in cookie:
                del cookie['logo_key']
            request.META['HTTP_COOKIE'] = '; '.join(['%s=%s' % (k, v.value) for k, v in cookie.items()])

        return HttpResponseRedirect(redirect_url)

    return _wrapped_view


def ajax_sso_required(view_func):

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated():
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("User must be authenticated to access this resource.")

    return _wrapped_view
