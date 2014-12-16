# coding: utf-8
from django.utils.decorators import method_decorator

from .decorators import sso_required


class SSORequiredMixin(object):

    @method_decorator(sso_required)
    def dispatch(self, *args, **kwargs):
        return super(SSORequiredMixin, self).dispatch(*args, **kwargs)
