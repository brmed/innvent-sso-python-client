# coding: utf-8
from django.urls import path
from ..views import forbidden


urlpatterns = [
    path('forbidden/', forbidden, name='forbidden_application'),
]
