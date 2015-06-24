# coding: utf-8
from django.conf.urls import patterns, url

from ..views import forbidden


urlpatterns = patterns('',
    url(r'forbidden/$', forbidden, name='forbidden_application'),
)

