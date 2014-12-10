# coding: utf-8
from django.conf.urls import patterns, url
from django.http import HttpResponse

from ..decorators import sso_required

@sso_required
def view(request):
    return HttpResponse('OK')

urlpatterns = patterns('',
    url(r'sso-required/$', view, name='sso_required'),
)
